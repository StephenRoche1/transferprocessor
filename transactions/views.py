import io
import requests
from django.core.checks import messages
from django.shortcuts import render
from .models import Transaction
import csv, json, xml
from django.views.generic.base import TemplateView
import xml.etree.ElementTree as ET
import pandas as pd



class AboutUs(TemplateView):
    template_name = 'index.html'


def profile_upload(request):
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    converter = RealTimeCurrencyConverter(url)
    template = "index.html"
    data = Transaction.objects.all()
    prompt = {
        'order': 'Order of the CSV should be id,source,dest,amount',
        'profiles': data
    }
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'Converting format to csv')
        if csv_file.name.endswith('.json'):
            df = pd.read_json(csv_file)
            csv_file = df.to_csv('csvfile.csv', encoding='utf-8', index=False)
        else:
            tree = ET.parse(csv_file)
            root = tree.getroot()

            get_range = lambda col: range(len(col))
            l = [{r[i].tag: r[i].text for i in get_range(r)} for r in root]

            df = pd.DataFrame.from_dict(l)
            csv_file = df.to_csv('csvfile.csv')
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for row in csv.reader(io_string, delimiter=',', quotechar="|"):
        fx = converter.convert(row[1], row[2], 1)
        created = Transaction.objects.create(
            Source=row[1],
            Destination=row[2],
            Amount=row[3],
            FX=fx,
            DestinationAmount=float(row[3]) * fx)
        created.save()
    context = {}
    return render(request, template, context)


class RealTimeCurrencyConverter:
    def __init__(self, url):
        self.data = requests.get(url).json()
        self.currencies = self.data['rates']

    def convert(self, from_currency, to_currency, amount):
        initial_amount = amount
        if from_currency != 'USD':
            amount = amount / self.currencies[from_currency]

        amount = round(amount * self.currencies[to_currency], 4)
        return amount
