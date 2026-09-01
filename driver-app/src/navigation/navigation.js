import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Linking
} from "react-native";

import MapView, {
  Marker,
  Polyline
} from "react-native-maps";

import * as Location from "expo-location";

import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = "http://192.168.1.100:8000";

export default function Navigation({ route, navigation }) {

  const ride =
    route?.params?.ride || null;

  const [driverLocation, setDriverLocation] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [locationSubscription, setLocationSubscription] =
    useState(null);

  const [rideStatus, setRideStatus] =
    useState(
      route?.params?.status || "accepted"
    );

  const mapRef = useRef(null);


  // ==================================================
  // GET TOKEN
  // ==================================================

  const getToken = async () => {

    return await AsyncStorage.getItem(
      "driver_token"
    );

  };


  // ==================================================
  // REQUEST LOCATION PERMISSION
  // ==================================================

  const requestLocationPermission =
    async () => {

      const { status } =
        await Location.requestForegroundPermissionsAsync();


      if (status !== "granted") {

        Alert.alert(
          "Location Permission Required",
          "RideX needs location permission for navigation."
        );

        return false;

      }

      return true;

    };


  // ==================================================
  // GET CURRENT LOCATION
  // ==================================================

  const getCurrentLocation = async () => {

    try {

      const permission =
        await requestLocationPermission();


      if (!permission) {

        return;

      }


      const current =
        await Location.getCurrentPositionAsync({

          accuracy:
            Location.Accuracy.High

        });


      const position = {

        latitude:
          current.coords.latitude,

        longitude:
          current.coords.longitude,

        accuracy:
          current.coords.accuracy

      };


      setDriverLocation(position);


      setLoading(false);


      return position;

    } catch (error) {

      console.error(
        "Current location error:",
        error
      );


      setLoading(false);


      Alert.alert(
        "Location Error",
        "Unable to determine your current location."
      );

    }

  };


  // ==================================================
  // SEND LOCATION TO BACKEND
  // ==================================================

  const sendLocationToBackend =
    async position => {

      try {

        const token =
          await getToken();

        const driverId =
          await AsyncStorage.getItem(
            "driver_id"
          );


        if (!driverId || !token) {

          return;

        }


        await fetch(

          `${API_URL}/api/v1/drivers/${driverId}/location`,

          {

            method: "POST",

            headers: {

              "Content-Type":
                "application/json",

              "Authorization":
                `Bearer ${token}`

            },

            body: JSON.stringify({

              latitude:
                position.latitude,

              longitude:
                position.longitude,

              accuracy:
                position.accuracy,

              ride_id:
                ride?.ride_id || null,

              timestamp:
                new Date().toISOString()

            })

          }

        );

      } catch (error) {

        console.error(
          "Location update error:",
          error
        );

      }

    };


  // ==================================================
  // START LOCATION TRACKING
  // ==================================================

  const startLocationTracking =
    async () => {

      const permission =
        await requestLocationPermission();


      if (!permission) {

        return;

      }


      const subscription =
        await Location.watchPositionAsync(

          {

            accuracy:
              Location.Accuracy.High,

            timeInterval:
              3000,

            distanceInterval:
              5

          },

          async position => {

            const newLocation = {

              latitude:
                position.coords.latitude,

              longitude:
                position.coords.longitude,

              accuracy:
                position.coords.accuracy

            };


            setDriverLocation(
              newLocation
            );


            await sendLocationToBackend(
              newLocation
            );


            // Keep driver centered on map

            if (mapRef.current) {

              mapRef.current.animateCamera(

                {

                  center: {

                    latitude:
                      newLocation.latitude,

                    longitude:
                      newLocation.longitude

                  }

                },

                {

                  duration: 500

                }

              );

            }

          }

        );


      setLocationSubscription(
        subscription
      );

    };


  // ==================================================
  // STOP LOCATION TRACKING
  // ==================================================

  const stopLocationTracking =
    () => {

      if (locationSubscription) {

        locationSubscription.remove();

        setLocationSubscription(
          null
        );

      }

    };


  // ==================================================
  // OPEN GOOGLE MAPS
  // ==================================================

  const openGoogleMaps =
    async () => {

      if (
        !driverLocation ||
        !ride?.pickup
      ) {

        Alert.alert(
          "Location Unavailable",
          "Driver or pickup location is unavailable."
        );

        return;

      }


      const destination =
        rideStatus === "started"
          ? ride.drop
          : ride.pickup;


      if (
        !destination?.latitude ||
        !destination?.longitude
      ) {

        Alert.alert(
          "Destination Unavailable",
          "Destination coordinates are missing."
        );

        return;

      }


      const url =
        `https://www.google.com/maps/dir/?api=1` +
        `&origin=${driverLocation.latitude},${driverLocation.longitude}` +
        `&destination=${destination.latitude},${destination.longitude}` +
        `&travelmode=driving`;


      try {

        await Linking.openURL(url);

      } catch (error) {

        Alert.alert(
          "Navigation Error",
          "Unable to open Google Maps."
        );

      }

    };


  // ==================================================
  // MARK DRIVER ARRIVED
  // ==================================================

  const markArrived = async () => {

    if (!ride?.ride_id) {

      return;

    }


    try {

      const token =
        await getToken();


      const response =
        await fetch(

          `${API_URL}/api/v1/rides/${ride.ride_id}/arrived`,

          {

            method: "POST",

            headers: {

              "Content-Type":
                "application/json",

              "Authorization":
                `Bearer ${token}`

            }

          }

        );


      if (!response.ok) {

        throw new Error(
          "Unable to update status"
        );

      }


      setRideStatus(
        "arrived"
      );


      Alert.alert(
        "Arrived",
        "Passenger has been notified that you arrived."
      );


    } catch (error) {

      console.error(
        "Arrived error:",
        error
      );


      Alert.alert(
        "Error",
        "Unable to update arrival status."
      );

    }

  };


  // ==================================================
  // START RIDE
  // ==================================================

  const startRide = async () => {

    if (!ride?.ride_id) {

      return;

    }


    try {

      const token =
        await getToken();


      const response =
        await fetch(

          `${API_URL}/api/v1/rides/${ride.ride_id}/start`,

          {

            method: "POST",

            headers: {

              "Content-Type":
                "application/json",

              "Authorization":
                `Bearer ${token}`

            }

          }

        );


      if (!response.ok) {

        throw new Error(
          "Unable to start ride"
        );

      }


      setRideStatus(
        "started"
      );


      Alert.alert(
        "Ride Started",
        "Navigation is now directed to the passenger destination."
      );


    } catch (error) {

      console.error(
        "Start ride error:",
        error
      );


      Alert.alert(
        "Error",
        "Unable to start the ride."
      );

    }

  };


  // ==================================================
  // COMPLETE RIDE
  // ==================================================

  const completeRide = async () => {

    if (!ride?.ride_id) {

      return;

    }


    try {

      const token =
        await getToken();


      const response =
        await fetch(

          `${API_URL}/api/v1/rides/${ride.ride_id}/complete`,

          {

            method: "POST",

            headers: {

              "Content-Type":
                "application/json",

              "Authorization":
                `Bearer ${token}`

            }

          }

        );


      if (!response.ok) {

        throw new Error(
          "Unable to complete ride"
        );

      }


      setRideStatus(
        "completed"
      );


      stopLocationTracking();


      Alert.alert(
        "Ride Completed",
        "Ride completed successfully."
      );


    } catch (error) {

      console.error(
        "Complete ride error:",
        error
      );


      Alert.alert(
        "Error",
        "Unable to complete the ride."
      );

    }

  };


  // ==================================================
  // INITIALIZE
  // ==================================================

  useEffect(() => {

    const initialize =
      async () => {

        await getCurrentLocation();

        await startLocationTracking();

      };


    initialize();


    return () => {

      if (locationSubscription) {

        locationSubscription.remove();

      }

    };

  }, []);


  // ==================================================
  // NO RIDE
  // ==================================================

  if (!ride) {

    return (

      <View style={styles.center}>

        <Text style={styles.title}>
          No Active Ride
        </Text>

        <Text style={styles.subtitle}>
          Accept a ride to start navigation.
        </Text>

      </View>

    );

  }


  // ==================================================
  // LOADING
  // ==================================================

  if (loading || !driverLocation) {

    return (

      <View style={styles.center}>

        <ActivityIndicator
          size="large"
        />

        <Text style={styles.loadingText}>
          Getting your location...
        </Text>

      </View>

    );

  }


  // ==================================================
  // DESTINATION
  // ==================================================

  const destination =
    rideStatus === "started"
      ? ride.drop
      : ride.pickup;


  // ==================================================
  // MAP REGION
  // ==================================================

  const initialRegion = {

    latitude:
      driverLocation.latitude,

    longitude:
      driverLocation.longitude,

    latitudeDelta:
      0.05,

    longitudeDelta:
      0.05

  };


  // ==================================================
  // SCREEN
  // ==================================================

  return (

    <View style={styles.container}>


      {/* MAP */}

      <MapView

        ref={mapRef}

        style={styles.map}

        initialRegion={initialRegion}

        showsUserLocation={true}

        showsMyLocationButton={true}

        followsUserLocation={false}

      >


        {/* Driver */}

        <Marker

          coordinate={{

            latitude:
              driverLocation.latitude,

            longitude:
              driverLocation.longitude

          }}

          title="You"

          description="Driver"

        />


        {/* Destination */}

        {destination &&
          destination.latitude &&
          destination.longitude && (

          <Marker

            coordinate={{

              latitude:
                destination.latitude,

              longitude:
                destination.longitude

            }}

            title={
              rideStatus === "started"
                ? "Destination"
                : "Pickup"
            }

          />

        )}


        {/* Straight-line visual */}

        {destination &&
          destination.latitude &&
          destination.longitude && (

          <Polyline

            coordinates={[

              {

                latitude:
                  driverLocation.latitude,

                longitude:
                  driverLocation.longitude

              },

              {

                latitude:
                  destination.latitude,

                longitude:
                  destination.longitude

              }

            ]}

            strokeWidth={4}

          />

        )}

      </MapView>


      {/* TOP STATUS */}

      <View style={styles.statusCard}>

        <Text style={styles.statusTitle}>

          {rideStatus === "started"
            ? "Navigate to Destination"
            : rideStatus === "arrived"
              ? "Waiting for Passenger"
              : "Navigate to Pickup"}

        </Text>


        <Text style={styles.statusAddress}>

          {destination.address ||
            "Destination"}

        </Text>

      </View>


      {/* RIDE INFORMATION */}

      <View style={styles.bottomCard}>


        <View style={styles.locationRow}>

          <View style={styles.dot} />

          <View style={styles.locationContent}>

            <Text style={styles.label}>

              {rideStatus === "started"
                ? "DESTINATION"
                : "PICKUP"}

            </Text>

            <Text style={styles.address}>

              {destination.address ||
                "Location unavailable"}

            </Text>

          </View>

        </View>


        <View style={styles.infoRow}>

          <View>

            <Text style={styles.infoLabel}>
              Passenger
            </Text>

            <Text style={styles.infoValue}>

              {ride.passenger?.name ||
                "Passenger"}

            </Text>

          </View>


          <View>

            <Text style={styles.infoLabel}>
              Fare
            </Text>

            <Text style={styles.fare}>

              ₹{ride.fare || "--"}

            </Text>

          </View>

        </View>


        {/* Google Maps */}

        <TouchableOpacity

          style={styles.navigationButton}

          onPress={openGoogleMaps}

        >

          <Text style={styles.buttonText}>

            Open Google Maps

          </Text>

        </TouchableOpacity>


        {/* Arrived */}

        {rideStatus === "accepted" && (

          <TouchableOpacity

            style={styles.secondaryButton}

            onPress={markArrived}

          >

            <Text style={styles.secondaryText}>

              I Have Arrived

            </Text>

          </TouchableOpacity>

        )}


        {/* Start Ride */}

        {rideStatus === "arrived" && (

          <TouchableOpacity

            style={styles.navigationButton}

            onPress={startRide}

          >

            <Text style={styles.buttonText}>

              Start Ride

            </Text>

          </TouchableOpacity>

        )}


        {/* Complete */}

        {rideStatus === "started" && (

          <TouchableOpacity

            style={styles.completeButton}

            onPress={completeRide}

          >

            <Text style={styles.buttonText}>

              Complete Ride

            </Text>

          </TouchableOpacity>

        )}

      </View>

    </View>

  );

}


// ==================================================
// STYLES
// ==================================================

const styles = StyleSheet.create({

  container: {

    flex: 1,

    backgroundColor: "#ffffff"

  },

  center: {

    flex: 1,

    justifyContent: "center",

    alignItems: "center",

    padding: 20

  },

  title: {

    fontSize: 25,

    fontWeight: "bold",

    marginBottom: 10

  },

  subtitle: {

    fontSize: 16,

    textAlign: "center"

  },

  loadingText: {

    marginTop: 15,

    fontSize: 16

  },

  map: {

    flex: 1

  },

  statusCard: {

    position: "absolute",

    top: 45,

    left: 15,

    right: 15,

    backgroundColor: "#ffffff",

    padding: 15,

    borderRadius: 10,

    elevation: 5

  },

  statusTitle: {

    fontSize: 18,

    fontWeight: "bold",

    marginBottom: 5

  },

  statusAddress: {

    fontSize: 14

  },

  bottomCard: {

    backgroundColor: "#ffffff",

    padding: 20,

    borderTopLeftRadius: 20,

    borderTopRightRadius: 20,

    elevation: 10

  },

  locationRow: {

    flexDirection: "row",

    alignItems: "flex-start"

  },

  dot: {

    width: 14,

    height: 14,

    borderRadius: 7,

    marginTop: 4,

    marginRight: 12,

    backgroundColor: "#000000"

  },

  locationContent: {

    flex: 1

  },

  label: {

    fontSize: 11,

    fontWeight: "bold",

    marginBottom: 5

  },

  address: {

    fontSize: 16,

    lineHeight: 21

  },

  infoRow: {

    flexDirection: "row",

    justifyContent: "space-between",

    marginTop: 18,

    paddingTop: 15,

    borderTopWidth: 1

  },

  infoLabel: {

    fontSize: 12,

    marginBottom: 4

  },

  infoValue: {

    fontSize: 16,

    fontWeight: "bold"

  },

  fare: {

    fontSize: 18,

    fontWeight: "bold"

  },

  navigationButton: {

    height: 52,

    backgroundColor: "#000000",

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center",

    marginTop: 18

  },

  secondaryButton: {

    height: 52,

    borderWidth: 1,

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center",

    marginTop: 10

  },

  secondaryText: {

    fontSize: 16,

    fontWeight: "bold"

  },

  completeButton: {

    height: 52,

    backgroundColor: "#000000",

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center",

    marginTop: 10

  },

  buttonText: {

    color: "#ffffff",

    fontSize: 16,

    fontWeight: "bold"

  }

});
