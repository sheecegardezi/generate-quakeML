"""
QUAKEML format
The QUAKEML format stores earthquake information in a hierarchical structure.
Each event is given as attributes a list of picks (station recording data), origins (hypocentres computed for the event based on observations), and magnitudes (calculated based on the signal strength at each station), as well as various other information.
Each origin is given a set of coordinates, a list of arrivals (pointers to the picks used in computation of the hypocentre location), and various other pieces of information.
QUAKEML files can be created using the python obspy library. I have previously done this by importing the following:
"""
from obspy import UTCDateTime
from obspy.geodetics.base import gps2dist_azimuth
from obspy.core.event import Catalog, Event, Origin, Pick, Arrival, CreationInfo, WaveformStreamID, EventDescription, QuantityError, OriginQuality, OriginUncertainty

"""

The minimum information we need for reprocessing and seismic tomography is the following:
    •	event_id (str): Event unique identifier
•	event_author_id (str): Event author identifier
•	event_agency_id (str): Event agency identifier (who created the event object)
•	event_type (str): Event type (mine blast, earthquake, etc.)
•	origin_id (str): Origin unique identifier
•	origin_time (float): Origin time
•	origin_longitude, origin_latitude, origin_depth (floats): Origin hypocentre longitude, latitude, and depth
•	origin_author_id (str): Origin author identifier
•	origin_agency_id (str): Origin agency identifier (who calculated the hypocentre)
•	pick_ids (list of str): Pick (recording) unique identifier
•	pick_arrival_times (list of float): Pick signal arrival time
•	pick_backazimuths (list of float): Pick backazimuth (direction signal arrived from)
•	pick_phases (list of str): Pick phase (pressure wave or shear wave)
•	pick_author_ids (list of str): Pick author identifier
•	pick_agency_ids (list of str): agency identifier (who recorded the signal)
•	pick_network_ids (list of str):Pick network code (network the recorder is on)
•	pick_station_ids (list of str): Pick station code (station the recorder is at)
•	pick_channel_ids (list of str): Pick channel code (channel the recorder is recording on, optional)
•	pick_station_latitudes (list of float)
•	pick_station_longitudes (list of float)

There should be pick information for each station that recorded the event. Also, there may be multiple origins if more than one person has computed the hypocentre. We only need one origin for tomography.
I have created event XML files before as follows. I first made an empty list, then populated it with 'Pick' objects (from obspy.core.event) corresponding to each station that recorded an event. I also make a list of 'Arrival' objects, to be appended to the preferred origin.
"""
# ########### #
# Inputs data #
# ########### #
picks = list()
arrivals = list()
olat = str()  # origin_latitude
olon = str()  # origin_longitude

# picks information
pick_ids = list()  # list of picks
pick_station_latitudes = []
pick_station_longitudes = []
pick_arrival_times = []
pick_backazimuths = []
pick_phases = []
pick_agency_ids = []
pick_author_ids = []
pick_network_ids = []
pick_station_ids = []
pick_channel_ids = []

# origin information
origin_id = None
origin_time = None
origin_longitude = None
origin_latitude = None
origin_depth = None
origin_author_id = None
origin_agency_id = None

# event information
event_id = None
event_agency_id = None
event_author_id = None
event_type = None

# ####### #
# Process #
# ####### #

# I then loop through all the information I have available to create the pick objects:
for i in range(len(pick_ids)):
    slat = pick_station_latitudes[i]
    slon = pick_station_longitudes[i]
    [distance, azimuth, _] = gps2dist_azimuth(olat, olon, slat, slon)
    Pick_object = Pick(
        resource_id=pick_ids[i],
        time=UTCDateTime(pick_arrival_times[i]),
        backazimuth=pick_backazimuths[i],
        phase_hint=pick_phases[i],
        creation_info=CreationInfo(agency_id=pick_agency_ids[i], author=pick_author_ids[i]),
        waveform_id=WaveformStreamID(network_code=pick_network_ids[i], station_code=pick_station_ids[i],
                                     channel_code=pick_channel_ids[i], location_code='—'),
        time_errors=QuantityError(),
        filter_id=None,
        method_id=None,
        horizontal_slowness=None,
        horizontal_slowness_errors=QuantityError(),
        backazimuth_errors=QuantityError(),
        slowness_method_id=None,
        onset=None,
        polarity=None,
        evaluation_mode=None,
        evaluation_status=None,
        comments=[]
    )
    picks.append(Pick_object)
    Arrival_object = Arrival(
        resource_id=str(pick_ids[i] + '_arrival'),
        pick_id=pick_ids[i],
        phase=pick_phases[i],
        azimuth=azimuth,
        distance=distance,
        creation_info=CreationInfo(agency_id=pick_agency_ids[i],
                                   author=pick_author_ids[i]),
        time_correction=None,
        takeoff_angle=None,
        takeoff_angle_errors=None,
        time_residual=None,
        horizontal_slowness_residual=None,
        backazimuth_residual=None,
        time_weight=None,
        horizontal_slowness_weight=None,
        backazimuth_weight=None,
        earth_model_id=None,
        comments=[]
    )
    arrivals.append(Arrival_object)
    # end for

# Then, I create an 'Origin' object to be the preferred origin for the event:
Origin_object = Origin(resource_id=origin_id,
                       time=UTCDateTime(origin_time),
                       longitude=origin_longitude,
                       latitude=origin_latitude,
                       depth=origin_depth,
                       creation_info=CreationInfo(author=origin_author_id, agency=origin_agency_id),
                       arrivals=arrivals,
                       time_errors=QuantityError(),
                       longitude_errors=QuantityError(),
                       latitude_errors=QuantityError(),
                       depth_errors=QuantityError(),
                       depth_type=None,
                       time_fixed=None,
                       epicenter_fixed=None,
                       reference_system_id=None,
                       method_id=None,
                       earth_model_id=None,
                       quality=OriginQuality(used_phase_count=None,
                                             standard_error=None,
                                             minimum_distance=None,
                                             maximum_distance=None),
                       origin_type=None,
                       origin_uncertainty=OriginUncertainty(min_horizontal_uncertainty=None,
                                                            max_horizontal_uncertainty=None,
                                                            azimuth_max_horizontal_uncertainty=None,
                                                            preferred_description=None),
                       region=None,
                       evaluation_mode=None,
                       evaluation_status=None,
                       comments=[],
                       composite_times=[])

# This origin, the picks, and the other event information are then put into an event object:
Event_object = Event(
    resource_id=event_id,
    preferred_origin_id=origin_id,
    picks=picks,
    amplitudes=list(),
    focal_mechanisms=list(),
    origins=[Origin_object],
    magnitudes=list(),
    station_magnitudes=list(),
    creation_info=CreationInfo(
        agency_id=event_agency_id,
        author=event_author_id,
        _format='SC3ML',
        event_type=event_type,
        event_type_certainty='known',
        preferred_magnitude_id=None,
        comments=None,
        event_descriptions=[list()]
    )
)

# ###### #
# Output #
# ###### #

# To write to disk, a catalogue is first created:
catalogue = Catalog(events=None)
# Then events can be appended to it:
catalogue.append(Event_object)
# And finally, the write function is called:
catalogue.write('filename.str', format='SC3ML')
# This will save the event catalogue in the 'SC3ML' format, which is similar to the QUAKEML format. #To save in the QUAKEML format, set format to 'QuakeML'.
