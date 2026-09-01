import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Linking
} from "react-native";

import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = "http://192.168.1.100:8000";

export default function AcceptRide({ route, navigation }) {

  const [ride, setRide] = useState(
    route?.params?.ride || null
  );

  const [loading, setLoading] =
    useState(false);

  const [rideStatus, setRideStatus] =
    useState("pending");


  // ==================================================
  // GET TOKEN
  // ==================================================

  const getToken = async () => {

    return await AsyncStorage.getItem(
      "driver_token"
    );

  };


  // ==================================================
  // ACCEPT RIDE
  // ==================================================

  const acceptRide = async () => {

    if (!ride?.ride_id) {

      Alert.alert(
        "Error",
        "Ride information is missing."
      );

      return;
    }


    try {

      setLoading(true);

      const token =
        await getToken();


      const response = await fetch(

        `${API_URL}/api/v1/rides/${ride.ride_id}/accept`,

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
              ride.ride_id

          })

        }

      );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Unable to accept ride"
        );

      }


      console.log(
        "Ride accepted:",
        data
      );


      setRideStatus(
        "accepted"
      );


      // Update ride information
      setRide({

        ...ride,

        ...data,

        status: "accepted"

      });


      Alert.alert(

        "Ride Accepted ✓",

        "You have been assigned this ride."

      );


    } catch (error) {

      console.error(
        "Accept ride error:",
        error
      );


      Alert.alert(

        "Ride Not Available",

        error.message ||
        "This ride may have already been accepted by another driver."

      );

    } finally {

      setLoading(false);

    }

  };


  // ==================================================
  // REJECT / CANCEL
  // ==================================================

  const rejectRide = async () => {

    if (!ride?.ride_id) {
      return;
    }


    try {

      setLoading(true);

      const token =
        await getToken();


      const response =
        await fetch(

          `${API_URL}/api/v1/rides/${ride.ride_id}/reject`,

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
                ride.ride_id

            })

          }

        );


      if (!response.ok) {

        throw new Error(
          "Unable to reject ride"
        );

      }


      setRideStatus(
        "rejected"
      );


      Alert.alert(

        "Ride Rejected",

        "The ride has been released.",

        [

          {

            text: "OK",

            onPress: () => {

              if (navigation) {

                navigation.goBack();

              }

            }

          }

        ]

      );


    } catch (error) {

      console.error(
        "Reject ride error:",
        error
      );


      Alert.alert(
        "Error",
        "Unable to reject the ride."
      );

    } finally {

      setLoading(false);

    }

  };


  // ==================================================
  // START NAVIGATION
  // ==================================================

  const startNavigation = () => {

    if (!ride?.pickup) {

      Alert.alert(
        "Location Missing",
        "Pickup location is unavailable."
      );

      return;

    }


    const latitude =
      ride.pickup.latitude;

    const longitude =
      ride.pickup.longitude;


    if (
      latitude === undefined ||
      longitude === undefined
    ) {

      Alert.alert(
        "Location Missing",
        "GPS coordinates are unavailable."
      );

      return;

    }


    const url =
      `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}&travelmode=driving`;


    Linking.openURL(url)
      .catch(error => {

        console.error(
          "Navigation error:",
          error
        );

        Alert.alert(
          "Navigation Error",
          "Unable to open navigation."
        );

      });

  };


  // ==================================================
  // MARK DRIVER ARRIVED
  // ==================================================

  const markDriverArrived = async () => {

    try {

      setLoading(true);

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
          "Unable to update ride status"
        );

      }


      setRideStatus(
        "arrived"
      );


      Alert.alert(

        "Driver Arrived",

        "You have arrived at the pickup location."

      );


    } catch (error) {

      console.error(
        "Arrival error:",
        error
      );


      Alert.alert(
        "Error",
        "Unable to update arrival status."
      );

    } finally {

      setLoading(false);

    }

  };


  // ==================================================
  // START RIDE
  // ==================================================

  const startRide = async () => {

    try {

      setLoading(true);

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

        "Passenger ride has started."

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

    } finally {

      setLoading(false);

    }

  };


  // ==================================================
  // COMPLETE RIDE
  // ==================================================

  const completeRide = async () => {

    try {

      setLoading(true);

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


      Alert.alert(

        "Ride Completed ✓",

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

    } finally {

      setLoading(false);

    }

  };


  // ==================================================
  // NO RIDE
  // ==================================================

  if (!ride) {

    return (

      <View style={styles.center}>

        <Text style={styles.title}>
          No Ride Selected
        </Text>

      </View>

    );

  }


  // ==================================================
  // REJECTED
  // ==================================================

  if (rideStatus === "rejected") {

    return (

      <View style={styles.center}>

        <Text style={styles.title}>
          Ride Rejected
        </Text>

        <Text style={styles.subtitle}>
          Waiting for another ride request.
        </Text>

      </View>

    );

  }


  // ==================================================
  // MAIN SCREEN
  // ==================================================

  return (

    <View style={styles.container}>


      <Text style={styles.title}>
        {rideStatus === "pending"
          ? "Confirm Ride"
          : "Active Ride"}
      </Text>


      {/* Status */}

      <View style={styles.statusCard}>

        <View
          style={[
            styles.statusDot,
            rideStatus === "accepted"
              ? styles.green
              : styles.orange
          ]}
        />

        <Text style={styles.statusText}>

          {rideStatus.toUpperCase()}

        </Text>

      </View>


      {/* Passenger */}

      <View style={styles.card}>

        <Text style={styles.sectionTitle}>
          Passenger
        </Text>


        <Text style={styles.passengerName}>

          {ride.passenger?.name ||
            "Passenger"}

        </Text>


        {ride.passenger?.phone && (

          <Text style={styles.detailText}>

            📞 {ride.passenger.phone}

          </Text>

        )}


        {ride.passenger?.rating && (

          <Text style={styles.detailText}>

            ⭐ {ride.passenger.rating}

          </Text>

        )}

      </View>


      {/* Pickup */}

      <View style={styles.card}>

        <Text style={styles.sectionTitle}>
          Pickup
        </Text>

        <Text style={styles.address}>

          📍{" "}
          {ride.pickup?.address ||
            "Pickup location"}

        </Text>

      </View>


      {/* Destination */}

      <View style={styles.card}>

        <Text style={styles.sectionTitle}>
          Destination
        </Text>

        <Text style={styles.address}>

          🏁{" "}
          {ride.drop?.address ||
            "Destination"}

        </Text>

      </View>


      {/* Ride Details */}

      <View style={styles.detailsCard}>


        <View style={styles.detailItem}>

          <Text style={styles.detailLabel}>
            Distance
          </Text>

          <Text style={styles.detailValue}>

            {ride.distance || "--"} km

          </Text>

        </View>


        <View style={styles.detailItem}>

          <Text style={styles.detailLabel}>
            Duration
          </Text>

          <Text style={styles.detailValue}>

            {ride.duration || "--"} min

          </Text>

        </View>


        <View style={styles.detailItem}>

          <Text style={styles.detailLabel}>
            Fare
          </Text>

          <Text style={styles.fare}>

            ₹{ride.fare || "--"}

          </Text>

        </View>

      </View>


      {/* Pending buttons */}

      {rideStatus === "pending" && (

        <View style={styles.buttonRow}>

          <TouchableOpacity

            style={styles.rejectButton}

            onPress={rejectRide}

            disabled={loading}

          >

            <Text style={styles.rejectText}>
              Reject
            </Text>

          </TouchableOpacity>


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

      )}


      {/* Accepted */}

      {rideStatus === "accepted" && (

        <>

          <TouchableOpacity

            style={styles.navigationButton}

            onPress={startNavigation}

          >

            <Text style={styles.buttonText}>
              Navigate to Pickup
            </Text>

          </TouchableOpacity>


          <TouchableOpacity

            style={styles.arrivedButton}

            onPress={markDriverArrived}

            disabled={loading}

          >

            <Text style={styles.arrivedText}>
              I Have Arrived
            </Text>

          </TouchableOpacity>

        </>

      )}


      {/* Arrived */}

      {rideStatus === "arrived" && (

        <TouchableOpacity

          style={styles.navigationButton}

          onPress={startRide}

          disabled={loading}

        >

          {loading ? (

            <ActivityIndicator
              color="#ffffff"
            />

          ) : (

            <Text style={styles.buttonText}>
              Start Ride
            </Text>

          )}

        </TouchableOpacity>

      )}


      {/* Started */}

      {rideStatus === "started" && (

        <>

          <TouchableOpacity

            style={styles.navigationButton}

            onPress={startNavigation}

          >

            <Text style={styles.buttonText}>
              Navigate to Destination
            </Text>

          </TouchableOpacity>


          <TouchableOpacity

            style={styles.completeButton}

            onPress={completeRide}

            disabled={loading}

          >

            {loading ? (

              <ActivityIndicator
                color="#ffffff"
              />

            ) : (

              <Text style={styles.buttonText}>
                Complete Ride
              </Text>

            )}

          </TouchableOpacity>

        </>

      )}


      {/* Completed */}

      {rideStatus === "completed" && (

        <View style={styles.completedCard}>

          <Text style={styles.completedTitle}>
            ✓ Ride Completed
          </Text>

          <Text style={styles.completedText}>

            Fare: ₹{ride.fare || "--"}

          </Text>

        </View>

      )}

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

  center: {

    flex: 1,

    justifyContent: "center",

    alignItems: "center",

    backgroundColor: "#ffffff"

  },

  title: {

    fontSize: 27,

    fontWeight: "bold",

    marginTop: 30,

    marginBottom: 15

  },

  subtitle: {

    fontSize: 16,

    marginTop: 10

  },

  statusCard: {

    flexDirection: "row",

    alignItems: "center",

    padding: 12,

    borderWidth: 1,

    borderRadius: 8,

    marginBottom: 12

  },

  statusDot: {

    width: 12,

    height: 12,

    borderRadius: 6,

    marginRight: 10

  },

  green: {

    backgroundColor: "green"

  },

  orange: {

    backgroundColor: "orange"

  },

  statusText: {

    fontWeight: "bold",

    fontSize: 14

  },

  card: {

    padding: 15,

    borderWidth: 1,

    borderRadius: 10,

    marginBottom: 10

  },

  sectionTitle: {

    fontSize: 12,

    fontWeight: "bold",

    marginBottom: 7

  },

  passengerName: {

    fontSize: 18,

    fontWeight: "bold"

  },

  detailText: {

    fontSize: 14,

    marginTop: 5

  },

  address: {

    fontSize: 16,

    lineHeight: 22

  },

  detailsCard: {

    flexDirection: "row",

    justifyContent: "space-between",

    padding: 15,

    borderWidth: 1,

    borderRadius: 10,

    marginTop: 5

  },

  detailItem: {

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

  buttonRow: {

    flexDirection: "row",

    gap: 10,

    marginTop: 20

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

  navigationButton: {

    height: 55,

    backgroundColor: "#000000",

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center",

    marginTop: 20

  },

  arrivedButton: {

    height: 55,

    borderWidth: 1,

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center",

    marginTop: 10

  },

  arrivedText: {

    fontSize: 17,

    fontWeight: "bold"

  },

  completeButton: {

    height: 55,

    backgroundColor: "#000000",

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center",

    marginTop: 10

  },

  buttonText: {

    color: "#ffffff",

    fontSize: 17,

    fontWeight: "bold"

  },

  completedCard: {

    padding: 20,

    borderWidth: 1,

    borderRadius: 10,

    marginTop: 20,

    alignItems: "center"

  },

  completedTitle: {

    fontSize: 20,

    fontWeight: "bold",

    marginBottom: 10

  },

  completedText: {

    fontSize: 18

  }

});
