import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert
} from "react-native";
import * as Location from "expo-location";

export default function PickupDrop() {
  const [pickup, setPickup] = useState("");
  const [drop, setDrop] = useState("");
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(false);

  // Get passenger's current GPS location
  const getCurrentLocation = async () => {
    try {
      setLoading(true);

      // Ask user for location permission
      const { status } =
        await Location.requestForegroundPermissionsAsync();

      if (status !== "granted") {
        Alert.alert(
          "Location Permission",
          "Please allow RideX to access your location."
        );
        return;
      }

      // Get current GPS coordinates
      const currentLocation =
        await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.High
        });

      const latitude = currentLocation.coords.latitude;
      const longitude = currentLocation.coords.longitude;

      setLocation({
        latitude,
        longitude
      });

      setPickup(
        `Current Location (${latitude.toFixed(6)}, ${longitude.toFixed(6)})`
      );

    } catch (error) {
      console.error("Location error:", error);

      Alert.alert(
        "Location Error",
        "Unable to get your current location."
      );

    } finally {
      setLoading(false);
    }
  };

  // Continue to fare estimation
  const handleContinue = () => {
    if (!pickup) {
      Alert.alert(
        "Pickup Required",
        "Please select your pickup location."
      );
      return;
    }

    if (!drop) {
      Alert.alert(
        "Destination Required",
        "Please enter your destination."
      );
      return;
    }

    console.log("Ride Request:");

    console.log({
      pickup,
      drop,
      location
    });

    Alert.alert(
      "Ride Details",
      `Pickup:\n${pickup}\n\nDrop:\n${drop}`
    );
  };

  return (
    <View style={styles.container}>

      <Text style={styles.title}>
        Where are you going?
      </Text>

      {/* Pickup */}
      <Text style={styles.label}>
        Pickup Location
      </Text>

      <TouchableOpacity
        style={styles.locationButton}
        onPress={getCurrentLocation}
      >
        <Text style={styles.locationButtonText}>
          {loading
            ? "Getting Location..."
            : "📍 Use Current Location"}
        </Text>
      </TouchableOpacity>

      <TextInput
        style={styles.input}
        placeholder="Pickup location"
        value={pickup}
        onChangeText={setPickup}
      />

      {/* Drop */}
      <Text style={styles.label}>
        Destination
      </Text>

      <TextInput
        style={styles.input}
        placeholder="Enter destination"
        value={drop}
        onChangeText={setDrop}
      />

      {/* Continue */}
      <TouchableOpacity
        style={styles.continueButton}
        onPress={handleContinue}
      >
        <Text style={styles.continueText}>
          Continue
        </Text>
      </TouchableOpacity>

      {/* GPS information */}
      {location && (
        <View style={styles.gpsBox}>
          <Text style={styles.gpsTitle}>
            GPS Coordinates
          </Text>

          <Text>
            Latitude: {location.latitude}
          </Text>

          <Text>
            Longitude: {location.longitude}
          </Text>
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
    fontSize: 26,
    fontWeight: "bold",
    marginTop: 40,
    marginBottom: 30
  },

  label: {
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 8,
    marginTop: 15
  },

  input: {
    height: 55,
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 15,
    fontSize: 16,
    marginBottom: 10
  },

  locationButton: {
    height: 50,
    borderWidth: 1,
    borderRadius: 8,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 10
  },

  locationButtonText: {
    fontSize: 16,
    fontWeight: "600"
  },

  continueButton: {
    height: 55,
    borderRadius: 8,
    backgroundColor: "#000000",
    justifyContent: "center",
    alignItems: "center",
    marginTop: 30
  },

  continueText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "bold"
  },

  gpsBox: {
    marginTop: 30,
    padding: 15,
    borderRadius: 8,
    borderWidth: 1
  },

  gpsTitle: {
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 8
  }

});
