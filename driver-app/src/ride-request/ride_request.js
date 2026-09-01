import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator
} from "react-native";

import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = "http://192.168.1.100:8000";
const WS_URL = "ws://192.168.1.100:8000";

export default function RideRequest() {

  const websocketRef = useRef(null);

  const [rideRequest, setRideRequest] =
    useState(null);

  const [connected, setConnected] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  // ==================================================
  // GET DRIVER ID
  // ==================================================

  const getDriverId = async () => {

    return await AsyncStorage.getItem(
      "driver_id"
    );

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
  // CONNECT TO RIDE REQUEST WEBSOCKET
  // ==================================================

  const connectWebSocket = async () => {

    const driverId =
      await getDriverId();

    const token =
      await getToken();


    if (!driverId || !token) {

      Alert.alert(
        "Login Required",
        "Please login as a driver first."
      );

      return;

    }


    const websocket =
      new WebSocket(
        `${WS_URL}/ws/drivers/${driverId}/rides?token=${token}`
      );


    websocketRef.current =
      websocket;


    // ------------------------------------------------
    // Connected
    // ------------------------------------------------

    websocket.onopen = () => {

      console.log(
        "Ride request WebSocket connected"
      );

      setConnected(true);

    };


    // ------------------------------------------------
    // Receive message
    // ------------------------------------------------

    websocket.onmessage = event => {

      try {

        const data =
          JSON.parse(event.data);

        console.log(
          "Ride request:",
          data
        );


        // New ride request

        if (
          data.type ===
          "ride_request"
        ) {

          setRideRequest({

            ride_id:
              data.ride_id,

            passenger:
              data.passenger,

            pickup:
              data.pickup,

            drop:
              data.drop,

            distance:
              data.distance,

            duration:
              data.duration,

            fare:
              data.fare,

            vehicle_type:
              data.vehicle_type

          });

        }


        // Ride cancelled

        if (
          data.type ===
          "ride_cancelled"
        ) {

          setRideRequest(null);

          Alert.alert(
            "Ride Cancelled",
            "The passenger cancelled the ride."
          );

        }

      } catch (error) {

        console.error(
          "WebSocket message error:",
          error
        );

      }

    };


    // ------------------------------------------------
    // Connection closed
    // ------------------------------------------------

    websocket.onclose = () => {

      console.log(
        "Ride request WebSocket disconnected"
      );

      setConnected(false);

    };


    // ------------------------------------------------
    // Error
    // ------------------------------------------------

    websocket.onerror = error => {

      console.error(
        "WebSocket error:",
        error
      );

      setConnected(false);

    };

  };


  // ==================================================
  // ACCEPT RIDE
  // ==================================================

  const acceptRide = async () => {

    if (!rideRequest) {
      return;
    }


    try {

      setLoading(true);


      const token =
        await getToken();


      const response =
        await fetch(

          `${API_URL}/api/v1/rides/${rideRequest.ride_id}/accept`,

          {

            method: "POST",

            headers: {

              "Content-Type":
                "application/json",

              "Authorization":
                `Bearer ${token}`

            },

            body: JSON.stringify({

              ride_id:
                rideRequest.ride_id

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
        "Ride accepted:",
        data
      );


      Alert.alert(
        "Ride Accepted",
        "Navigate to the passenger pickup location."
      );


      // Send acceptance through WebSocket

      if (
        websocketRef.current &&
        websocketRef.current.readyState === 1
      ) {

        websocketRef.current.send(

          JSON.stringify({

            type:
              "ride_accepted",

            ride_id:
              rideRequest.ride_id

          })

        );

      }


      // Keep accepted ride for next screen
      setRideRequest({

        ...rideRequest,

        status: "accepted"

      });


    } catch (error) {

      console.error(
        "Accept ride error:",
        error
      );


      Alert.alert(
        "Unable to Accept",
        "This ride may have already been assigned to another driver."
      );

    } finally {

      setLoading(false);

    }

  };


  // ==================================================
  // REJECT RIDE
  // ==================================================

  const rejectRide = async () => {

    if (!rideRequest) {
      return;
    }


    try {

      setLoading(true);


      const token =
        await getToken();


      const response =
        await fetch(

          `${API_URL}/api/v1/rides/${rideRequest.ride_id}/reject`,

          {

            method: "POST",

            headers: {

              "Content-Type":
                "application/json",

              "Authorization":
                `Bearer ${token}`

            },

            body: JSON.stringify({

              ride_id:
                rideRequest.ride_id

            })

          }

        );


      if (!response.ok) {

        throw new Error(
          `HTTP ${response.status}`
        );

      }


      console.log(
        "Ride rejected"
      );


      // Notify backend through WebSocket

      if (
        websocketRef.current &&
        websocketRef.current.readyState === 1
      ) {

        websocketRef.current.send(

          JSON.stringify({

            type:
              "ride_rejected",

            ride_id:
              rideRequest.ride_id

          })

        );

      }


      setRideRequest(null);


    } catch (error) {

      console.error(
        "Reject ride error:",
        error
      );


      Alert.alert(
        "Error",
        "Unable to reject this ride."
      );

    } finally {

      setLoading(false);

    }

  };


  // ==================================================
  // CONNECT WHEN SCREEN OPENS
  // ==================================================

  useEffect(() => {

    connectWebSocket();


    return () => {

      if (
        websocketRef.current
      ) {

        websocketRef.current.close();

        websocketRef.current =
          null;

      }

    };

  }, []);


  // ==================================================
  // NO RIDE REQUEST
  // ==================================================

  if (!rideRequest) {

    return (

      <View style={styles.emptyContainer}>

        <Text style={styles.logo}>
          RideX
        </Text>

        <Text style={styles.title}>
          Ride Requests
        </Text>


        <View style={styles.connectionBox}>

          <View
            style={[
              styles.statusDot,

              connected
                ? styles.online
                : styles.offline
            ]}
          />

          <Text>

            {connected
              ? "Waiting for ride requests..."
              : "Connecting to RideX..."}

          </Text>

        </View>


        {!connected && (

          <TouchableOpacity
            style={styles.retryButton}
            onPress={connectWebSocket}
          >

            <Text style={styles.retryText}>
              Reconnect
            </Text>

          </TouchableOpacity>

        )}

      </View>

    );

  }


  // ==================================================
  // ACCEPTED RIDE
  // ==================================================

  if (
    rideRequest.status ===
    "accepted"
  ) {

    return (

      <View style={styles.emptyContainer}>

        <Text style={styles.logo}>
          RideX
        </Text>

        <Text style={styles.acceptedTitle}>
          Ride Accepted ✓
        </Text>


        <View style={styles.acceptedCard}>

          <Text style={styles.acceptedText}>

            Pickup

          </Text>

          <Text style={styles.address}>

            {rideRequest.pickup.address}

          </Text>


          <Text style={styles.acceptedText}>

            Destination

          </Text>

          <Text style={styles.address}>

            {rideRequest.drop.address}

          </Text>

        </View>


        <TouchableOpacity
          style={styles.navigationButton}
          onPress={() => {

            Alert.alert(
              "Navigation",
              "Navigation screen will open here."
            );

          }}
        >

          <Text style={styles.buttonText}>
            Start Navigation
          </Text>

        </TouchableOpacity>

      </View>

    );

  }


  // ==================================================
  // RIDE REQUEST SCREEN
  // ==================================================

  return (

    <View style={styles.container}>

      <Text style={styles.title}>
        New Ride Request
      </Text>


      {/* Passenger */}

      <View style={styles.passengerCard}>

        <View style={styles.avatar}>

          <Text style={styles.avatarText}>
            {rideRequest.passenger?.name
              ?.charAt(0)
              || "P"}
          </Text>

        </View>


        <View>

          <Text style={styles.passengerName}>

            {rideRequest.passenger?.name
              || "Passenger"}

          </Text>


          {rideRequest.passenger?.rating && (

            <Text style={styles.rating}>

              ⭐{" "}
              {rideRequest.passenger.rating}

            </Text>

          )}

        </View>

      </View>


      {/* Pickup */}

      <View style={styles.locationCard}>

        <Text style={styles.locationLabel}>
          PICKUP
        </Text>

        <Text style={styles.locationAddress}>

          📍{" "}
          {rideRequest.pickup.address}

        </Text>

      </View>


      {/* Destination */}

      <View style={styles.locationCard}>

        <Text style={styles.locationLabel}>
          DESTINATION
        </Text>

        <Text style={styles.locationAddress}>

          📍{" "}
          {rideRequest.drop.address}

        </Text>

      </View>


      {/* Ride details */}

      <View style={styles.detailsCard}>


        <View style={styles.detail}>

          <Text style={styles.detailLabel}>
            Distance
          </Text>

          <Text style={styles.detailValue}>

            {rideRequest.distance}
            {" "}km

          </Text>

        </View>


        <View style={styles.detail}>

          <Text style={styles.detailLabel}>
            Estimated Time
          </Text>

          <Text style={styles.detailValue}>

            {rideRequest.duration}
            {" "}min

          </Text>

        </View>


        <View style={styles.detail}>

          <Text style={styles.detailLabel}>
            Fare
          </Text>

          <Text style={styles.fare}>

            ₹{rideRequest.fare}

          </Text>

        </View>

      </View>


      {/* Buttons */}

      <View style={styles.buttonsContainer}>


        {/* Reject */}

        <TouchableOpacity

          style={styles.rejectButton}

          onPress={rejectRide}

          disabled={loading}

        >

          <Text style={styles.rejectText}>
            Reject
          </Text>

        </TouchableOpacity>


        {/* Accept */}

        <TouchableOpacity

          style={styles.acceptButton}

          onPress={acceptRide}

          disabled={loading}

        >

          {loading ? (

            <ActivityIndicator
              color="#ffffff"
            />

          ) : (

            <Text style={styles.buttonText}>
              Accept Ride
            </Text>

          )}

        </TouchableOpacity>

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

    padding: 20,

    backgroundColor: "#ffffff"

  },

  emptyContainer: {

    flex: 1,

    padding: 25,

    justifyContent: "center",

    alignItems: "center",

    backgroundColor: "#ffffff"

  },

  logo: {

    fontSize: 40,

    fontWeight: "bold",

    marginBottom: 10

  },

  title: {

    fontSize: 27,

    fontWeight: "bold",

    marginTop: 35,

    marginBottom: 20

  },

  connectionBox: {

    flexDirection: "row",

    alignItems: "center",

    padding: 15,

    borderWidth: 1,

    borderRadius: 10

  },

  statusDot: {

    width: 10,

    height: 10,

    borderRadius: 5,

    marginRight: 10

  },

  online: {

    backgroundColor: "green"

  },

  offline: {

    backgroundColor: "gray"

  },

  retryButton: {

    marginTop: 20,

    padding: 15,

    borderWidth: 1,

    borderRadius: 8

  },

  retryText: {

    fontWeight: "bold"

  },

  passengerCard: {

    flexDirection: "row",

    alignItems: "center",

    padding: 15,

    borderWidth: 1,

    borderRadius: 10,

    marginBottom: 15

  },

  avatar: {

    width: 50,

    height: 50,

    borderRadius: 25,

    backgroundColor: "#eeeeee",

    justifyContent: "center",

    alignItems: "center",

    marginRight: 15

  },

  avatarText: {

    fontSize: 22,

    fontWeight: "bold"

  },

  passengerName: {

    fontSize: 18,

    fontWeight: "bold"

  },

  rating: {

    marginTop: 4

  },

  locationCard: {

    padding: 16,

    borderWidth: 1,

    borderRadius: 10,

    marginBottom: 12

  },

  locationLabel: {

    fontSize: 12,

    fontWeight: "bold",

    marginBottom: 8

  },

  locationAddress: {

    fontSize: 16

  },

  detailsCard: {

    flexDirection: "row",

    justifyContent: "space-between",

    padding: 18,

    borderWidth: 1,

    borderRadius: 10,

    marginTop: 5

  },

  detail: {

    alignItems: "center"

  },

  detailLabel: {

    fontSize: 12,

    marginBottom: 5

  },

  detailValue: {

    fontSize: 16,

    fontWeight: "bold"

  },

  fare: {

    fontSize: 18,

    fontWeight: "bold"

  },

  buttonsContainer: {

    flexDirection: "row",

    gap: 12,

    marginTop: 25

  },

  rejectButton: {

    flex: 1,

    height: 55,

    borderWidth: 1,

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center"

  },

  rejectText: {

    fontSize: 17,

    fontWeight: "bold"

  },

  acceptButton: {

    flex: 2,

    height: 55,

    backgroundColor: "#000000",

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center"

  },

  buttonText: {

    color: "#ffffff",

    fontSize: 17,

    fontWeight: "bold"

  },

  acceptedTitle: {

    fontSize: 25,

    fontWeight: "bold",

    marginBottom: 25

  },

  acceptedCard: {

    width: "100%",

    padding: 20,

    borderWidth: 1,

    borderRadius: 10

  },

  acceptedText: {

    fontSize: 13,

    fontWeight: "bold",

    marginTop: 10

  },

  address: {

    fontSize: 16,

    marginTop: 6

  },

  navigationButton: {

    width: "100%",

    height: 55,

    backgroundColor: "#000000",

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center",

    marginTop: 25

  }

});
