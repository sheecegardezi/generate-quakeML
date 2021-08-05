import pickle
import requests
import logging


def get_list_of_events(start_time, end_time):
    url = "https://earthquakes.ga.gov.au/geoserver/earthquakes/wfs?service=WFS&request=getfeature&typeNames=earthquakes:earthquakes&outputFormat=application/json&CQL_FILTER=display_flag=%27Y%27%20AND%20located_in_australia=%27Y%27%20AND%20preferred_magnitude%3E=0%20AND%20preferred_magnitude%3C=9.94%20AND%20origin_time%20BETWEEN%20" + start_time + "Z%20AND%20" + end_time + "Z"
    response = requests.get(url)
    return response.json()


def get_earthquakes_focal_mechanism(earthquake_id):
    url = "https://earthquakes.ga.gov.au/geoserver/earthquakes/wfs?service=WFS&request=getfeature&typeNames=earthquakes:earthquakes_focal_mechanism&outputFormat=application/json&CQL_FILTER=earthquake_id=" + str(earthquake_id)
    response = requests.get(url)
    return response.json()


def get_earthquakes_shakemap(event_id):
    url = "https://earthquakes.ga.gov.au/geoserver/earthquakes/wfs?service=WFS&request=getfeature&typeNames=earthquakes:shakemap&outputFormat=application/json&CQL_FILTER=event_id=%27" + str(event_id) + "%27&dt=1625543755701"
    response = requests.get(url)
    return response.json()


def get_felt_reports(event_id):
    url = "https://earthquakes.ga.gov.au/geoserver/earthquakes/wfs?service=WFS&request=getfeature&typeNames=earthquakes:earthquakes_felt_reports&outputFormat=application/json&CQL_FILTER=event_id=" + "'" + event_id + "'"
    response = requests.get(url)
    return response.json()


def get_trace_diagram(event_id):
    url = "https://cdn.eatws.net/skip/events/" + event_id + "/traces.png"
    open('traces.png', 'wb').write(requests.get(url, allow_redirects=True).content)
    print('file saved: traces.png')


def get_station_information(earthquake_id):
    url = "https://earthquakes.ga.gov.au/geoserver/earthquakes/wfs?service=WFS&request=getfeature&typeNames=earthquakes:earthquakes_stations&outputFormat=application/json&CQL_FILTER=earthquake_id=" + str(earthquake_id)
    response = requests.get(url)
    return response.json()


def get_magnitudes_information(earthquake_id):
    url = "https://earthquakes.ga.gov.au/geoserver/earthquakes/wfs?service=WFS&request=getfeature&typeNames=earthquakes:earthquakes_magnitude&outputFormat=application/json&CQL_FILTER=earthquake_id=" + str(earthquake_id)
    response = requests.get(url)
    return response.json()


def get_event_information(event_details):

    event_data = {}

    event_data["event_details"] = event_details
    earthquake_id = event_details["properties"]["earthquake_id"]
    event_id = event_details["properties"]["event_id"]

    logging.info("Getting focal mechanism information")
    focal_mechanism_information = get_earthquakes_focal_mechanism(earthquake_id)
    event_data["focal_mechanism_information"] = focal_mechanism_information

    logging.info("Getting Shakemap information")
    shakemap_information = get_earthquakes_shakemap(event_id)
    event_data["shakemap_information"] = shakemap_information

    logging.info("Getting Felt Reports")
    felt_reports = get_felt_reports(event_id)
    event_data["felt_reports"] = felt_reports

    logging.info("Getting trace diagram")
    get_trace_diagram(event_id)
    event_data["trace_diagram"] = "path to trace diagram"

    logging.info("Getting station information")
    station_information = get_station_information(earthquake_id)
    event_data["station_information"] = station_information

    logging.info("Getting magnitudes information")
    magnitudes_information = get_magnitudes_information(earthquake_id)
    event_data["magnitudes_information"] = magnitudes_information

    return event_data


def get_events(start_time="2020-06-24T09:27:00", end_time="2021-06-24T09:27:00"):
    # TODO implement bounding box constraint on events
    bounding_box = None
    list_of_events = get_list_of_events(start_time, end_time)["features"]

    logging.info("Getting event details")
    for event_details in list_of_events:
        event_data = get_event_information(event_details)
        # print(event_data)
        return event_data
        break


if __name__ == '__main__':
    event_data = get_events(start_time="2020-06-24T09:27:00", end_time="2021-06-24T09:27:00")

    with open('C:/Users/sheec/Desktop/Project/genquakeml/data/test_event.pkl', 'wb') as handle:
        pickle.dump(event_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # with open('data/test_event.pkl', 'rb') as handle:
    #     b = pickle.load(handle)
