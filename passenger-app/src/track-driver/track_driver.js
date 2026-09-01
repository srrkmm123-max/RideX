import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator
} from "react-native";

import MapView, {
  Marker,
  Polyline
} from "react-native-maps";

import * as Location from "expo-location";

const API_URL = "http://192.168.1.100:8000";
const WS_URL = "ws://192.168.1.100:8000";

const RIDE_ID = 1;

export default function TrackDriver() {

  const mapRef = useRef(null);
  const websocketRef = useRef(null);

  const [passengerLocation, setPassengerLocation] =
    useState(null);

  const [driverLocation, setDriverLocation] =
    useState(null);

  const [driver, setDriver] = useState({
    name: "Loading...",
    rating: 0,
    vehicle: "Loading...",
    type: "Bike"
  });

  const [distance, setDistance] =
    useState(null);

  const [eta, setEta] =
    useState(null);

  const [connected, setConnected] =
    useState(false);

  const [loading, setLoading] =
    useState(true);


  // ==================================================
  // GET PASSENGER LOCATION
  // ==================================================

  const getPassengerLocation = async () => {

    try {

      const { status } =
        await Location.requestForegroundPermissionsAsync();

      if (status !== "granted") {

        Alert.alert(
          "Location Permission",
          "Please allow RideX to access your location."
        );

        return;
      }

      const location =
        await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.High
        });

      const position = {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude
      };

      setPassengerLocation(position);

      return position;

    } catch (error) {

      console.error(
        "Passenger location error:",
        error
      );

      Alert.alert(
        "Location Error",
        "Unable to determine your location."
      );

    } finally {

      setLoading(false);

    }
  };


  // ==================================================
  // GET DRIVER INFORMATION
  // ==================================================

  const getDriverInformation = async () => {

    try {

      const response = await fetch(
        `${API_URL}/api/v1/rides/${RIDE_ID}/driver`
      );

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}`
        );
      }

      const data = await response.json();

      console.log(
        "Driver information:",
        data
      );

      if (data.driver) {

        setDriver(data.driver);

      }

      if (data.location) {

        setDriverLocation({
          latitude: data.location.latitude,
          longitude: data.location.longitude
        });

      }

      if (data.distance !== undefined) {

        setDistance(data.distance);

      }

      if (data.eta !== undefined) {

        setEta(data.eta);

      }

    } catch (error) {

      console.error(
        "Driver API error:",
        error
      );

    }

  };


  // ==================================================
  // CONNECT WEBSOCKET
  // ==================================================

  const connectWebSocket = () => {

    const websocket =
      new WebSocket(
        `${WS_URL}/ws/rides/${RIDE_ID}`
      );

    websocketRef.current = websocket;


    // Connected
    websocket.onopen = () => {

      console.log(
        "RideX WebSocket connected"
      );

      setConnected(true);

    };


    // Receive driver GPS updates
    websocket.onmessage = (event) => {

      try {

        const data =
          JSON.parse(event.data);

        console.log(
          "WebSocket data:",
          data
        );


        // Driver location
        if (data.type === "driver_location") {

          const newLocation = {

            latitude:
              Number(data.latitude),

            longitude:
              Number(data.longitude)

          };

          setDriverLocation(
            newLocation
          );


          // Update map camera
          if (mapRef.current) {

            mapRef.current.animateToRegion(
              {
                ...newLocation,
                latitudeDelta: 0.02,
                longitudeDelta: 0.02
              },
              500
            );

          }

        }


        // ETA update
        if (data.type === "eta_update") {

          setEta(data.eta);

        }


        // Distance update
        if (data.type === "distance_update") {

          setDistance(data.distance);

        }


        // Driver information
        if (data.type === "driver_update") {

          setDriver(
            previous => ({
              ...previous,
              ...data.driver
            })
          );

        }


        // Ride completed
        if (data.type === "ride_completed") {

          Alert.alert(
            "Ride Completed",
            "Your RideX trip has been completed."
          );

        }

      } catch (error) {

        console.error(
          "WebSocket message error:",
          error
        );

      }

    };


    // Connection closed
    websocket.onclose = () => {

      console.log(
        "RideX WebSocket disconnected"
      );

      setConnected(false);

    };


    // WebSocket error
    websocket.onerror = (error) => {

      console.error(
        "WebSocket error:",
        error
      );

      setConnected(false);

    };

  };


  // ==================================================
  // INITIALIZE
  // ==================================================

  useEffect(() => {

    let mounted = true;


    const initialize = async () => {

      await getPassengerLocation();

      if (!mounted) {
        return;
      }

      await getDriverInformation();

      if (!mounted) {
        return;
      }

      connectWebSocket();

    };


    initialize();


    // Cleanup
    return () => {

      mounted = false;

      if (websocketRef.current) {

        websocketRef.current.close();

        websocketRef.current = null;

      }

    };

  }, []);


  // ==================================================
  // RECENTER MAP
  // ==================================================

  const centerOnDriver = () => {

    if (
      !driverLocation ||
      !mapRef.current
    ) {
      return;
    }

    mapRef.current.animateToRegion(
      {
        ...driverLocation,

        latitudeDelta: 0.02,

        longitudeDelta: 0.02

      },

      500

    );

  };


  // ==================================================
  // LOADING SCREEN
  // ==================================================

  if (loading) {

    return (

      <View style={styles.loadingContainer}>

        <ActivityIndicator
          size="large"
        />

        <Text style={styles.loadingText}>
          Loading RideX...
        </Text>

      </View>

    );

  }


  // ==================================================
  // MAIN SCREEN
  // ==================================================

  return (

    <View style={styles.container}>


      {/* Header */}

      <View style={styles.header}>

        <Text style={styles.title}>
          Your Driver
        </Text>

        <View style={styles.connectionRow}>

          <View
            style={[
              styles.statusDot,
              connected
                ? styles.connected
                : styles.disconnected
            ]}
          />

          <Text style={styles.connectionText}>

            {connected
              ? "Live"
              : "Connecting..."}

          </Text>

        </View>

      </View>


      {/* Driver Information */}

      <View style={styles.driverCard}>

        <View>

          <Text style={styles.driverName}>
            {driver.name}
          </Text>

          <Text style={styles.driverInfo}>
            ⭐ {driver.rating}
          </Text>

          <Text style={styles.driverInfo}>
            🏍️ {driver.vehicle}
          </Text>

          <Text style={styles.driverInfo}>
            {driver.type}
          </Text>

        </View>


        <View style={styles.etaContainer}>

          <Text style={styles.eta}>

            {eta !== null
              ? eta
              : "--"}

          </Text>

          <Text style={styles.etaLabel}>
            min
          </Text>

        </View>

      </View>


      {/* Map */}

      <View style={styles.mapContainer}>

        {passengerLocation ? (

          <MapView

            ref={mapRef}

            style={styles.map}

            initialRegion={{

              latitude:
                passengerLocation.latitude,

              longitude:
                passengerLocation.longitude,

              latitudeDelta: 0.03,

              longitudeDelta: 0.03

            }}

            showsUserLocation={true}

            showsMyLocationButton={true}

          >


            {/* Passenger */}

            <Marker

              coordinate={
                passengerLocation
              }

              title="You"

              description="Passenger"

            />


            {/* Driver */}

            {driverLocation && (

              <Marker

                coordinate={
                  driverLocation
                }

                title={driver.name}

                description="Your Driver"

              />

            )}


            {/* Driver → Passenger line */}

            {driverLocation && (

              <Polyline

                coordinates={[
                  passengerLocation,
                  driverLocation
                ]}

                strokeWidth={4}

              />

            )}

          </MapView>

        ) : (

          <View style={styles.noMap}>

            <Text>
              Passenger location unavailable
            </Text>

          </View>

        )}

      </View>


      {/* Distance */}

      <View style={styles.distanceCard}>

        <Text style={styles.distanceText}>

          Driver is approximately{" "}

          <Text style={styles.bold}>

            {distance !== null
              ? `${distance} km`
              : "--"}

          </Text>

          {" "}away

        </Text>

      </View>


      {/* Recenter */}

      <TouchableOpacity

        style={styles.recenterButton}

        onPress={centerOnDriver}

      >

        <Text style={styles.recenterText}>
          📍 Center on Driver
        </Text>

      </TouchableOpacity>


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

  loadingContainer: {

    flex: 1,

    justifyContent: "center",

    alignItems: "center"

  },

  loadingText: {

    marginTop: 10,

    fontSize: 16

  },

  header: {

    marginTop: 45,

    marginHorizontal: 20,

    marginBottom: 15,

    flexDirection: "row",

    justifyContent: "space-between",

    alignItems: "center"

  },

  title: {

    fontSize: 26,

    fontWeight: "bold"

  },

  connectionRow: {

    flexDirection: "row",

    alignItems: "center"

  },

  statusDot: {

    width: 9,

    height: 9,

    borderRadius: 5,

    marginRight: 5

  },

  connected: {

    backgroundColor: "green"

  },

  disconnected: {

    backgroundColor: "gray"

  },

  connectionText: {

    fontSize: 13

  },

  driverCard: {

    marginHorizontal: 20,

    padding: 15,

    borderWidth: 1,

    borderRadius: 10,

    flexDirection: "row",

    justifyContent: "space-between",

    alignItems: "center"

  },

  driverName: {

    fontSize: 20,

    fontWeight: "bold",

    marginBottom: 5

  },

  driverInfo: {

    fontSize: 14,

    marginTop: 3

  },

  etaContainer: {

    alignItems: "center"

  },

  eta: {

    fontSize: 32,

    fontWeight: "bold"

  },

  etaLabel: {

    fontSize: 14

  },

  mapContainer: {

    height: 400,

    marginTop: 15,

    marginHorizontal: 15,

    borderRadius: 10,

    overflow: "hidden"

  },

  map: {

    flex: 1

  },

  noMap: {

    flex: 1,

    justifyContent: "center",

    alignItems: "center"

  },

  distanceCard: {

    padding: 15,

    alignItems: "center"

  },

  distanceText: {

    fontSize: 16

  },

  bold: {

    fontWeight: "bold"

  },

  recenterButton: {

    height: 50,

    marginHorizontal: 20,

    borderWidth: 1,

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center"

  },

  recenterText: {

    fontSize: 16,

    fontWeight: "bold"

  }

});
