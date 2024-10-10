#! /usr/bin/env python3
import argparse
import csv
import rosbag
import utm
from tf.transformations import euler_from_quaternion

#BROKEN BROKEN BROKEN BROKEN

def main():
    """
    bag_file is an input that reads the path to the bag file
    output_file is an argument that reads the path to the output file
    subsample is the number of points to be selected to be converted to waypoints
    """
    # Read in bag path from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("bag_file", help="Path to bag file")
    parser.add_argument("output_file", help="Path to output file")
    parser.add_argument(
        "subsample", help="Subsample rate (1 = don't skip any waypoints)", type=int
    )
    args = parser.parse_args()

    # Open bag
    bag = rosbag.Bag(args.bag_file)

    # Create data structure
    waypoints = []

    # Track index for skipping waypoints
    i = 0

    # Loop through bag
    for _, msg, time in bag.read_messages(topics="/NAND/nav/odom"):
        # Skip waypoints
        if i % args.subsample != 0:
            i += 1
            continue
        i += 1
        # print(type(time))
        # print(type(msg))
        # print("time, ", time.to_sec())
        # print("msg, ", msg)
        # TODO: Check Orientation
        lat = msg.pose.pose.position.y
        lon = msg.pose.pose.position.x
        # print(utm.from_latlon(lat, lon))
        easting, northing, _, _ = utm.from_latlon(lat, lon)
        orientation_q = msg.pose.pose.orientation

        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (_, _, yaw) = euler_from_quaternion (orientation_list)
        speed = msg.twist.twist.linear.x


        waypoints.append([str(time.to_sec()), str(northing), str(easting), str(yaw), str(speed),])

    # Write to csv file
    with open(args.output_file, "w", newline="") as csvfile:
        writer = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        writer.writerow(["Time (s)", "Northing (m)", "Easting (m)", "Yaw (rad)", "Speed (m/s)"])
        for row in waypoints:
            writer.writerow(row)


if __name__ == "__main__":
    main()
