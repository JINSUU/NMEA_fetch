import serial
import time
import os
from datetime import datetime, timedelta, timezone
import traceback

port = 'COM3'
ser = serial.Serial(port, 9600, timeout=1)

time.sleep(2)  # wait after initiating

NMEA_START = '$G'
DTS_set = ['GGA', 'GLL', 'GSA', 'GSV', 'RMC', 'VTG', 'ZDA', 'GSV']
CHECKSUM_PREFIX = '*'

local_time = datetime.now()
local_tzinfo = local_time.tzinfo

# NMEA: National Marine Electronics Association

# Reference
# https://receiverhelp.trimble.com/alloy-gnss/en-us/nmea0183-messages-overview.html

while True:
    response = ser.readline()
    if response:
        try:
            NMEA = response.decode().strip()

            if NMEA.startswith(NMEA_START) and CHECKSUM_PREFIX in NMEA:

                raw_data, checksum = NMEA.split(CHECKSUM_PREFIX)

                data = raw_data.split(',')

                Message_Type = data[0][3:6]

                match Message_Type:

                    case 'GGA': # Time, position, and fix related data

                        (Message_ID, UTC_of_position_fix, Latitude, Direction_of_latitude, Longitude,
                         Direction_of_longitude, GPS_Quality_indicator, Number_of_SVs_in_use, HDOP,
                         Orthometric_height, unit_of_measure_for_orthometric_height, Geoid_separation,
                         Unit_of_measure_for_geoid_separation, Age_of_differential_GPS_data_record,
                         Reference_station_ID, *GGA_extra) = data
                        
                        if GPS_Quality_indicator:
                            pass


                    case 'GSA': # GPS DOP and active satellites

                        (Message_ID, Mode_1, Mode_2, PRN_number, PDOP, HDOP, VDOP, *GSA_extra) = data


                    case 'GLL':  # Position data: position fix, time of position fix, and status

                        (Message_ID, Latitude, Direction_of_latitude,
                         Longitude, Direction_of_longitude, UTC_of_position,
                         Status, *GLL_extra) = data
                        
                        # print("Message ID:", Message_ID)
                        # print("Latitude:", Latitude)
                        # print("Direction of Latitude:", Direction_of_latitude)
                        # print("Longitude:", Longitude)
                        # print("Direction of Longitude:", Direction_of_longitude)
                        # print("UTC of Position:", UTC_of_position)
                        # print("Status:", Status)
                        # print("GLL Extra:", GLL_extra)

                    case 'RMC':  # Position, velocity, and time

                        os.system('cls')

                        (Message_ID, UTC_of_position_fix, Status, Latitude, _, 
                         Longitude, _, Speed_over_the_ground_in_knots, Track_angle_in_degrees,
                         UTC_date_str, Magnetic_variation, *RMC_extra) = data
                        
                        if UTC_of_position_fix and UTC_date_str:
                            utc_datetime = datetime.strptime(
                                UTC_date_str + UTC_of_position_fix[:-3],'%d%m%y%H%M%S').replace(
                                microsecond=int(UTC_of_position_fix[-2:]), tzinfo=timezone.utc,)
                            local_datetime = utc_datetime.astimezone(local_tzinfo)
                            print(f"UTC:{utc_datetime} / LOCAL:{local_datetime}")

                        # print("Message ID:", Message_ID)
                        # print("UTC of Position Fix:", UTC_of_position_fix)
                        # print("Status:", Status)
                        # print("Latitude:", Latitude)
                        # print("Longitude:", Longitude)
                        # print("Speed Over the Ground in Knots:", Speed_over_the_ground_in_knots)
                        # print("Track Angle in Degrees:", Track_angle_in_degrees)
                        # print("UTC Date String:", UTC_date_str)
                        # print("Magnetic Variation:", Magnetic_variation)
                        # print("RMC Extra:", RMC_extra)


                    case 'VTG':  # Track made good and speed over ground

                        (Message_ID, Track_made_good_along_true_north, _,
                         Track_made_good_along_magnetic_north, _, speed, knots_unit,
                         speed_over_ground_in_kph, kph_unit, Mode_indicator, *VTG_extra) = data

                        match (Mode_indicator):
                             case 'A': # Autonomous mode
                                  pass
                             case 'D': # Differential mode
                                  pass
                             case 'E': # Estimated (dead reckoning) mode
                                  pass
                             case 'M': # Manual Input mode
                                  pass
                             case 'S': # Simulator mode
                                  pass
                             case 'N': # Data not valid
                                  pass
                             case _:
                                  raise ValueError(f"Unavailable Mode_indicator - VTG, {Mode_indicator}")
                            
                        # print("Message ID:", Message_ID)
                        # print("Track Made Good Along True North:", Track_made_good_along_true_north)
                        # print("Track Made Good Along Magnetic North:", Track_made_good_along_magnetic_north)
                        # print("Speed:", speed)
                        # print("Knots Unit:", knots_unit)
                        # print("Speed Over Ground in KPH:", speed_over_ground_in_kph)
                        # print("KPH Unit:", kph_unit)
                        # print("Mode Indicator:", Mode_indicator)
                        # print("VTG Extra:", VTG_extra)

                    case 'ZDA':  # UTC day, month, and year, and local time zone offset

                        (Message_ID, UTC, Day, Month, Year,
                         Local_time_zone_hour_offset_from_GMT,
                         Local_time_zone_minute_offset_from_GMT,
                         *ZDA_extra) = data
                        
                        # print("Message ID:", Message_ID)
                        # print("UTC:", UTC)
                        # print("Day:", Day)
                        # print("Month:", Month)
                        # print("Year:", Year)
                        # print("Local Time Zone Hour Offset from GMT:", Local_time_zone_hour_offset_from_GMT)
                        # print("Local Time Zone Minute Offset from GMT:", Local_time_zone_minute_offset_from_GMT)
                        # print("ZDA Extra:", ZDA_extra)


                    case 'GSV': # Satellite information

                        (Message_ID, Total_number_of_messages_of_this_type_in_this_cycle,
                         Message_number, Total_number_of_SVs_visible, SV_PRN_number,
                         Elevation, Azimuth, SNR, *GSV_data) = data
                        
                        # print("Message ID:", Message_ID)
                        # print("Total number of messages of this type in this cycle:", Total_number_of_messages_of_this_type_in_this_cycle)
                        # print("Message number:", Message_number)
                        # print("Total number of SVs visible:", Total_number_of_SVs_visible)
                        # print("SV PRN number:", SV_PRN_number)
                        # print("Elevation:", Elevation)
                        # print("Azimuth:", Azimuth)
                        # print("SNR:", SNR)
                        # print("GSV data:", GSV_data)
                        
                    case _:  # Undefined Type
                        print(f"Unknown sentence type: {Message_Type}")

                print(data)

        except Exception as e:
            Error_Msg = traceback.format_exc()
            print(Error_Msg)
