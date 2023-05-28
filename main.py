import os
import datetime
import teslapy
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
tesla = teslapy.Tesla(os.environ['API_USER'], retry=3, timeout=20)


@app.template_filter()
def format_timestamp(value):
    datet = datetime.datetime.fromtimestamp(value / 1e3)
    return datet.strftime("%Y-%m-%d, %H:%M:%S %Z")


@app.route("/")
def home():
    vehicles = tesla.vehicle_list()
    vehicle_data = vehicles[0].get_vehicle_data()
    return render_template('index.html',
                           current_charger_state=vehicle_data.get('charge_state'),
                           climate_state=vehicle_data.get('climate_state'))


@app.route("/info")
def demo():
    vehicles = tesla.vehicle_list()
    return vehicles[0].get_vehicle_data()


@app.route("/set_charging_amps", methods=['POST'])
def set_charging_amps():
    new_value = request.form["chargerAmpsValue"]
    vehicles = tesla.vehicle_list()
    print('Setting charging amps to: ' + new_value + ' A')
    vehicles[0].command('CHARGING_AMPS', charging_amps=new_value)
    return redirect("/")


if __name__ == "__main__":
    if not tesla.authorized:
        print('Use browser to login. Page Not Found will be shown at success.')
        print('Open this URL: ' + tesla.authorization_url())
        tesla.fetch_token(authorization_response=input('Enter URL after authentication: '))

    app.run(host='0.0.0.0', debug=True)
