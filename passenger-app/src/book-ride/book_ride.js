import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator
} from "react-native";
import axios from "axios";

const API_URL = "http://192.168.1.100:8000";

export default function BookRide() {
  const [loading, setLoading] = useState(false);
  const [ride, setRide] = useState(null);

  // Sample ride information.
  // Later these values should come from pickup_drop.js
  // and fare_estimate.js.
  const rideRequest = {
    passenger_id: 1,

    pickup: {
      address: "Hyderabad Airport",
      latitude: 17.2403,
      longitude: 78.4294
    },

    drop: {
      address: "Hitech City",
      latitude: 17.4435,
      longitude: 78.3772
    },

    vehicle_type: "bike"
  };

  const bookRide = async () => {
    try {
      setLoading(true);

      const response = await axios.post(
        `${API_URL}/api/v1/rides`,
        rideRequest
      );

      console.log("Ride response:", response.data);

      setRide(response.data);

      Alert.alert(
        "Ride Requested",
        "Searching for a nearby driver..."
      );

    } catch (error) {
      console.error("Book ride error:", error);

      Alert.alert(
        "Booking Failed",
        "Unable to create the ride request. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };

  const cancelRide = async () => {
    if (!ride?.id) {
      setRide(null);
      return;
    }

    try {
      setLoading(true);

      await axios.post(
        `${API_URL}/api/v1/rides/${ride.id}/cancel`
      );

      setRide(null);

      Alert.alert(
        "Ride Cancelled",
        "Your ride has been cancelled."
      );

    } catch (error) {
      console.error("Cancel ride error:", error);

      Alert.alert(
        "Error",
        "Unable to cancel the ride."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>

      <Text style={styles.title}>
        Book Ride
      </Text>

      {/* Pickup */}
      <View style={styles.locationBox}>

        <Text style={styles.label}>
          PICKUP
        </Text>

        <Text style={styles.location}>
          📍 {rideRequest.pickup.address}
        </Text>

      </View>

      {/* Drop */}
      <View style={styles.locationBox}>

        <Text style={styles.label}>
          DROP
        </Text>

        <Text style={styles.location}>
          📍 {rideRequest.drop.address}
        </Text>

      </View>

      {/* Vehicle */}
      <View style={styles.infoBox}>

        <Text style={styles.infoLabel}>
          Vehicle
        </Text>

        <Text style={styles.infoValue}>
          🏍️ Bike
        </Text>

      </View>

      {/* Estimated Fare */}
      <View style={styles.infoBox}>

        <Text style={styles.infoLabel}>
          Estimated Fare
        </Text>

        <Text style={styles.fare}>
          ₹210
        </Text>

      </View>

      {!ride ? (

        <TouchableOpacity
          style={styles.bookButton}
          onPress={bookRide}
          disabled={loading}
        >

          {loading ? (
            <ActivityIndicator color="#ffffff" />
          ) : (
            <Text style={styles.buttonText}>
              Book Ride
            </Text>
          )}

        </TouchableOpacity>

      ) : (

        <View>

          <View style={styles.statusBox}>

            <Text style={styles.statusTitle}>
              Ride Requested
            </Text>

            <Text style={styles.status}>
              Searching for a nearby driver...
            </Text>

            <Text style={styles.rideId}>
              Ride ID: {ride.id}
            </Text>

          </View>

          <TouchableOpacity
            style={styles.cancelButton}
            onPress={cancelRide}
            disabled={loading}
          >

            <Text style={styles.cancelText}>
              Cancel Ride
            </Text>

          </TouchableOpacity>

        </View>

      )}

    </View>
  );
}

const styles = StyleSheet.create({

  container: {
    flex: 1,
    padding: 25,
    backgroundColor: "#ffffff"
  },

  title: {
    fontSize: 28,
    fontWeight: "bold",
    marginTop: 40,
    marginBottom: 30
  },

  locationBox: {
    padding: 18,
    borderWidth: 1,
    borderRadius: 10,
    marginBottom: 15
  },

  label: {
    fontSize: 12,
    fontWeight: "bold",
    marginBottom: 8
  },

  location: {
    fontSize: 17
  },

  infoBox: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 18,
    borderBottomWidth: 1
  },

  infoLabel: {
    fontSize: 16
  },

  infoValue: {
    fontSize: 16,
    fontWeight: "bold"
  },

  fare: {
    fontSize: 22,
    fontWeight: "bold"
  },

  bookButton: {
    height: 55,
    backgroundColor: "#000000",
    borderRadius: 8,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 35
  },

  buttonText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "bold"
  },

  statusBox: {
    marginTop: 30,
    padding: 20,
    borderWidth: 1,
    borderRadius: 10,
    alignItems: "center"
  },

  statusTitle: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 10
  },

  status: {
    fontSize: 15,
    marginBottom: 10
  },

  rideId: {
    fontSize: 13
  },

  cancelButton: {
    height: 50,
    borderWidth: 1,
    borderRadius: 8,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 15
  },

  cancelText: {
    fontSize: 17,
    fontWeight: "bold"
  }

});
