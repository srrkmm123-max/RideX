import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator
} from "react-native";

import * as Location from "expo-location";
import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = "http://192.168.1.100:8000";
const WS_URL = "ws://192.168.1.100:8000";

export default function DriverStatus() {

  const [isOnline, setIsOnline] = useState(false);

  const [location, setLocation] = useState(null);

  const [loading, setLoading] = useState(false);

  const [connected, setConnected] = useState(false);

  const websocketRef = useRef(null);

  const locationSubscriptionRef = useRef(null);


  // ==================================================
  // GET DRIVER ID
  // ==================================================

  const getDriverId = async () => {

    const driverId =
      await AsyncStorage.getItem("driver_id");

    return driverId;
  };


  // ==================================================
  // GET AUTH TOKEN
  // ==================================================

  const getToken = async () => {

    return await AsyncStorage.getItem(
      "driver_token"
    );
  };


  // ==================================================
  // REQUEST LOCATION PERMISSION
  // ==================================================

  const requestLocationPermission = async () => {

    const { status } =
      await Location.requestForegroundPermissionsAsync();

    if (status !== "granted") {

      Alert.alert(
        "Location Permission Required",
        "RideX needs your location to receive rides."
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
        return null;
      }

      const currentLocation =
        await Location.getCurrentPositionAsync({

          accuracy:
            Location.Accuracy.High

        });


      const newLocation = {

        latitude:
          currentLocation.coords.latitude,

        longitude:
          currentLocation.coords.longitude,

        accuracy:
          currentLocation.coords.accuracy

      };


      setLocation(newLocation);

      return newLocation;

    } catch (error) {

      console.error(
        "Location error:",
        error
      );

      Alert.alert(
        "Location Error",
        "Unable to get your current location."
      );

      return null;
    }
  };


  // ==================================================
  // UPDATE DRIVER STATUS IN BACKEND
  // ==================================================

  const updateDriverStatus = async (
    online
  ) => {

    try {

      const token =
        await getToken();

      const response = await fetch(
        `${API_URL}/api/v1/drivers/status`,
        {
          method: "POST",

          headers: {

            "Content-Type":
              "application/json",

            "Authorization":
              `Bearer ${token}`

          },

          body: JSON.stringify({

            online: online

          })

        }
      );


      if (!response.ok) {

        throw new Error(
          `HTTP ${response.status}`
        );

      }


      const data =
        await response.json();

      console.log(
        "Driver status:",
        data
      );


    } catch (error) {

      console.error(
        "Status API error:",
        error
      );

      throw error;
    }
  };


  // ==================================================
  // SEND GPS LOCATION TO BACKEND
  // ==================================================

  const sendLocationToBackend = async (
    newLocation
  ) => {

    try {

      const token =
        await getToken();

      const driverId =
        await getDriverId();


      const response =
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
                newLocation.latitude,

              longitude:
                newLocation.longitude,

              accuracy:
                newLocation.accuracy,

              timestamp:
                new Date().toISOString()

            })

          }
        );


      if (!response.ok) {

        throw new Error(
          `HTTP ${response.status}`
        );

      }


      console.log(
        "GPS location sent"
      );


    } catch (error) {

      console.error(
        "GPS API error:",
        error
      );

    }
  };


  // ==================================================
  // CONNECT WEBSOCKET
  // ==================================================

  const connectWebSocket = async () => {

    const driverId =
      await getDriverId();

    const token =
      await getToken();


    if (!driverId || !token) {

      console.error(
        "Driver authentication information missing."
      );

      return;
    }


    const websocket =
      new WebSocket(
        `${WS_URL}/ws/drivers/${driverId}?token=${token}`
      );


    websocketRef.current =
      websocket;


    websocket.onopen = () => {

      console.log(
        "Driver WebSocket connected"
      );

      setConnected(true);

    };


    websocket.onmessage = event => {

      try {

        const data =
          JSON.parse(event.data);

        console.log(
          "WebSocket message:",
          data
        );


        // Example:
        // Matching service can send
        // new ride notifications here.

        if (
          data.type ===
          "ride_request"
        ) {

          Alert.alert(
            "New Ride Request",
            `Pickup: ${data.pickup}\nDestination: ${data.drop}`
          );

        }

      } catch (error) {

        console.error(
          "WebSocket message error:",
          error
        );

      }

    };


    websocket.onclose = () => {

      console.log(
        "Driver WebSocket disconnected"
      );

      setConnected(false);

    };


    websocket.onerror = error => {

      console.error(
        "WebSocket error:",
        error
      );

      setConnected(false);

    };

  };


  // ==================================================
  // START LOCATION WATCHING
  // ==================================================

  const startLocationTracking = async () => {

    const permission =
      await requestLocationPermission();

    if (!permission) {
      return;
    }


    // Stop existing subscription
    if (
      locationSubscriptionRef.current
    ) {

      locationSubscriptionRef.current.remove();

    }


    locationSubscriptionRef.current =
      await Location.watchPositionAsync(

        {

          accuracy:
            Location.Accuracy.High,

          timeInterval:
            5000,

          distanceInterval:
            10

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


          setLocation(
            newLocation
          );


          // Send GPS to backend
          await sendLocationToBackend(
            newLocation
          );


          // Send GPS through WebSocket
          if (
            websocketRef.current &&
            websocketRef.current.readyState === 1
          ) {

            websocketRef.current.send(

              JSON.stringify({

                type:
                  "driver_location",

                latitude:
                  newLocation.latitude,

                longitude:
                  newLocation.longitude,

                accuracy:
                  newLocation.accuracy,

                timestamp:
                  new Date().toISOString()

              })

            );

          }

        }

      );

  };


  // ==================================================
  // STOP LOCATION TRACKING
  // ==================================================

  const stopLocationTracking = () => {

    if (
      locationSubscriptionRef.current
    ) {

      locationSubscriptionRef.current.remove();

      locationSubscriptionRef.current =
        null;

    }

  };


  // ==================================================
  // GO ONLINE
  // ==================================================

  const goOnline = async () => {

    try {

      setLoading(true);


      const permission =
        await requestLocationPermission();

      if (!permission) {
        return;
      }


      const currentLocation =
        await getCurrentLocation();

      if (!currentLocation) {
        return;
      }


      // Update backend status
      await updateDriverStatus(
        true
      );


      // Send first location
      await sendLocationToBackend(
        currentLocation
      );


      // Connect real-time channel
      await connectWebSocket();


      // Start continuous GPS
      await startLocationTracking();


      setIsOnline(true);


      await AsyncStorage.setItem(
        "driver_online",
        "true"
      );


      Alert.alert(
        "You're Online",
        "You can now receive ride requests."
      );


    } catch (error) {

      console.error(
        "Go online error:",
        error
      );


      Alert.alert(
        "Unable to Go Online",
        "Please try again."
      );

    } finally {

      setLoading(false);

    }

  };


  // ==================================================
  // GO OFFLINE
  // ==================================================

  const goOffline = async () => {

    try {

      setLoading(true);


      // Stop GPS
      stopLocationTracking();


      // Close WebSocket
      if (
        websocketRef.current
      ) {

        websocketRef.current.close();

        websocketRef.current =
          null;

      }


      setConnected(false);


      // Update backend
      await updateDriverStatus(
        false
      );


      setIsOnline(false);


      await AsyncStorage.setItem(
        "driver_online",
        "false"
      );


      Alert.alert(
        "You're Offline",
        "You will no longer receive ride requests."
      );


    } catch (error) {

      console.error(
        "Go offline error:",
        error
      );


      Alert.alert(
        "Unable to Go Offline",
        "Please try again."
      );

    } finally {

      setLoading(false);

    }

  };


  // ==================================================
  // LOAD SAVED STATUS
  // ==================================================

  useEffect(() => {

    const loadStatus = async () => {

      const savedStatus =
        await AsyncStorage.getItem(
          "driver_online"
        );


      if (savedStatus === "true") {

        setIsOnline(true);

        await connectWebSocket();

        await startLocationTracking();

      }

    };


    loadStatus();


    // Cleanup
    return () => {

      stopLocationTracking();


      if (
        websocketRef.current
      ) {

        websocketRef.current.close();

      }

    };

  }, []);


  // ==================================================
  // UI
  // ==================================================

  return (

    <View style={styles.container}>


      <Text style={styles.logo}>
        RideX
      </Text>


      <Text style={styles.title}>
        Driver Status
      </Text>


      {/* Status indicator */}

      <View style={styles.statusCard}>

        <View
          style={[
            styles.statusCircle,
            isOnline
              ? styles.onlineCircle
              : styles.offlineCircle
          ]}
        />

        <View>

          <Text style={styles.statusTitle}>

            {isOnline
              ? "ONLINE"
              : "OFFLINE"}

          </Text>

          <Text style={styles.statusText}>

            {isOnline
              ? "You can receive ride requests"
              : "You are not receiving rides"}

          </Text>

        </View>

      </View>


      {/* Connection */}

      {isOnline && (

        <View style={styles.connection}>

          <View
            style={[
              styles.connectionDot,
              connected
                ? styles.onlineCircle
                : styles.offlineCircle
            ]}
          />

          <Text>

            {connected
              ? "Real-time connection active"
              : "Connecting..."}

          </Text>

        </View>

      )}


      {/* GPS */}

      {location && (

        <View style={styles.locationCard}>

          <Text style={styles.locationTitle}>
            Current Location
          </Text>

          <Text>
            Latitude:{" "}
            {location.latitude.toFixed(6)}
          </Text>

          <Text>
            Longitude:{" "}
            {location.longitude.toFixed(6)}
          </Text>

          {location.accuracy && (

            <Text>
              Accuracy:{" "}
              {location.accuracy.toFixed(1)} m
            </Text>

          )}

        </View>

      )}


      {/* Online / Offline button */}

      <TouchableOpacity

        style={[
          styles.mainButton,
          isOnline
            ? styles.offlineButton
            : styles.onlineButton
        ]}

        onPress={
          isOnline
            ? goOffline
            : goOnline
        }

        disabled={loading}

      >

        {loading ? (

          <ActivityIndicator
            color="#ffffff"
          />

        ) : (

          <Text style={styles.buttonText}>

            {isOnline
              ? "GO OFFLINE"
              : "GO ONLINE"}

          </Text>

        )}

      </TouchableOpacity>


      {/* Information */}

      <Text style={styles.info}>

        {isOnline
          ? "Keep RideX open and location enabled to receive nearby ride requests."
          : "Go online when you are ready to accept passengers."}

      </Text>

    </View>

  );

}


// ==================================================
// STYLES
// ==================================================

const styles = StyleSheet.create({

  container: {

    flex: 1,

    padding: 25,

    backgroundColor: "#ffffff",

    justifyContent: "center"

  },

  logo: {

    fontSize: 42,

    fontWeight: "bold",

    textAlign: "center",

    marginBottom: 5

  },

  title: {

    fontSize: 27,

    fontWeight: "bold",

    textAlign: "center",

    marginBottom: 30

  },

  statusCard: {

    flexDirection: "row",

    alignItems: "center",

    padding: 20,

    borderWidth: 1,

    borderRadius: 10,

    marginBottom: 15

  },

  statusCircle: {

    width: 25,

    height: 25,

    borderRadius: 13,

    marginRight: 15

  },

  onlineCircle: {

    backgroundColor: "green"

  },

  offlineCircle: {

    backgroundColor: "gray"

  },

  statusTitle: {

    fontSize: 20,

    fontWeight: "bold"

  },

  statusText: {

    fontSize: 14,

    marginTop: 4

  },

  connection: {

    flexDirection: "row",

    alignItems: "center",

    padding: 12,

    marginBottom: 15

  },

  connectionDot: {

    width: 10,

    height: 10,

    borderRadius: 5,

    marginRight: 8

  },

  locationCard: {

    padding: 18,

    borderWidth: 1,

    borderRadius: 10,

    marginBottom: 20

  },

  locationTitle: {

    fontSize: 17,

    fontWeight: "bold",

    marginBottom: 8

  },

  mainButton: {

    height: 60,

    borderRadius: 10,

    justifyContent: "center",

    alignItems: "center"

  },

  onlineButton: {

    backgroundColor: "#000000"

  },

  offlineButton: {

    backgroundColor: "#555555"

  },

  buttonText: {

    color: "#ffffff",

    fontSize: 19,

    fontWeight: "bold"

  },

  info: {

    textAlign: "center",

    fontSize: 14,

    marginTop: 20,

    lineHeight: 20

  }

});
