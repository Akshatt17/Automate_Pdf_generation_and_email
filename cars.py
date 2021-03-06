#!/usr/bin/env python3
import emails
import os
import reports
import json
import locale
import sys


def load_data(filename):
  """Loads the contents of filename as a JSON file."""
  with open(filename) as json_file:
    data = json.load(json_file)
  return data


def format_car(car):
  """Given a car dictionary, returns a nicely formatted name."""
  return "{} {} ({})".format(
      car["car_make"], car["car_model"], car["car_year"])
def car_year(car):
  return car["car_year"]
def process_data(data):
  """Analyzes the data, looking for maximums.
  Returns a list of lines that summarize the information.
  """
  locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
  sales_freq={}
  max_revenue = {"revenue": 0}
  pop_year=0
  pop_sale=0
  max_sale=0
  max_sale_year=0
  for item in data:
    # Calculate the revenue generated by this model (price * total_sales)
    # We need to convert the price from "$1234.56" to 1234.56
    item_price = locale.atof(item["price"].strip("$"))
    item_revenue = item["total_sales"] * item_price
    if item_revenue > max_revenue["revenue"]:
      item["revenue"] = item_revenue
      max_revenue = item
    # handle max sales
    item_sale= item["total_sales"]
    if item_sale > max_sale:
       max_sale= item_sale
       max_sale_year = format_car(item["car"])
    # handle most popular car_year
    year=car_year(item["car"])
    if year in sales_freq:
       sales_freq[year] = item["total_sales"]+ sales_freq[year]
    else:
       sales_freq[year] = item["total_sales"]
    for y , s in sales_freq.items():
     if pop_sale< s:
        pop_sale=s
        pop_year=y

  summary = [
    "The {} generated the most revenue: ${}".format(
      format_car(max_revenue["car"]), max_revenue["revenue"]),
    "The {} had the most sales: {}".format(max_sale_year, max_sale),
    "The most popular year was {} with {} sales".format(pop_year, pop_sale)
  ]


  return summary

def cars_dict_to_table(car_data):
  """Turns the data in car_data into a list of lists."""
  table_data = [["ID", "Car", "Price", "Total Sales"]]
  for item in car_data:
    table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
  return table_data

def main(argv):
  """Process the JSON data and generate a full report out of it."""
  data = load_data("car_sales.json")
  summary = process_data(data)
  print(summary)
  table_data= cars_dict_to_table(data)
  # turn this into a PDF report
  reports.generate("/tmp/cars.pdf", "Sales summary for last month", summary[0] +"<br/>"+summary[1] +"<br/>" + summary[2],table_data)
  # send the PDF report as an email attachment
  sender = "sender_email@gmail.com"
  receiver = "reciever_email@gmail.com"
  subject = "Sales summary for last month"
  body = summary[0] +"\n"+summary[1] +"\n" + summary[2]
  message = emails.generate(sender, receiver, subject, body, "/tmp/cars.pdf")
  emails.send(message)

if __name__ == "__main__":
  main(sys.argv)


