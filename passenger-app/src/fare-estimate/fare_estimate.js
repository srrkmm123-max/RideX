import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert
} from "react-native";

export default function FareEstimate() {
  const [distance, setDistance] = useState("");
  const [duration, setDuration] = useState("");
  const [fare, setFare] = useState(null);

  // RideX pricing rules
  const BASE_FARE = 40;
  const PRICE_PER_KM = 12;
  const PRICE_PER_MINUTE = 2;

  // Change this later based on real-time demand
  const SURGE_MULTIPLIER = 1.0;

  const calculateFare = () => {
    const distanceKm = parseFloat(distance);
    const durationMin = parseFloat(duration);

    if (isNaN(distanceKm) || distanceKm <= 0) {
      Alert.alert(
        "Invalid Distance",
        "Please enter a valid distance."
      );
      return;
    }

    if (isNaN(durationMin) || durationMin <= 0) {
      Alert.alert(
        "Invalid Duration",
        "Please enter a valid travel time."
      );
      return;
    }

    const distanceFare = distanceKm * PRICE_PER_KM;
    const timeFare = durationMin * PRICE_PER_MINUTE;

    const subtotal =
      BASE_FARE +
      distanceFare +
      timeFare;

    const totalFare =
      subtotal * SURGE_MULTIPLIER;

    setFare(Math.round(totalFare));
  };

  return (
    <View style={styles.container}>

      <Text style={styles.title}>
        Fare Estimate
      </Text>

      <Text style={styles.subtitle}>
        Estimate your RideX trip cost
      </Text>

      {/* Distance */}
      <Text style={styles.label}>
        Distance (km)
      </Text>

      <TextInput
        style={styles.input}
        placeholder="Example: 10"
        keyboardType="numeric"
        value={distance}
        onChangeText={setDistance}
      />

      {/* Duration */}
      <Text style={styles.label}>
        Estimated Time (minutes)
      </Text>

      <TextInput
        style={styles.input}
        placeholder="Example: 25"
        keyboardType="numeric"
        value={duration}
        onChangeText={setDuration}
      />

      {/* Calculate */}
      <TouchableOpacity
        style={styles.button}
        onPress={calculateFare}
      >
        <Text style={styles.buttonText}>
          Calculate Fare
        </Text>
      </TouchableOpacity>

      {/* Result */}
      {fare !== null && (
        <View style={styles.result}>

          <Text style={styles.resultTitle}>
            Estimated Fare
          </Text>

          <Text style={styles.fare}>
            ₹{fare}
          </Text>

          <View style={styles.breakdown}>

            <Text>
              Base Fare: ₹{BASE_FARE}
            </Text>

            <Text>
              Distance: ₹
              {Math.round(
                parseFloat(distance) * PRICE_PER_KM
              )}
            </Text>

            <Text>
              Time: ₹
              {Math.round(
                parseFloat(duration) * PRICE_PER_MINUTE
              )}
            </Text>

            <Text>
              Surge: {SURGE_MULTIPLIER}x
            </Text>

          </View>

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
    marginTop: 40
  },

  subtitle: {
    fontSize: 16,
    marginTop: 8,
    marginBottom: 30
  },

  label: {
    fontSize: 16,
    fontWeight: "bold",
    marginTop: 15,
    marginBottom: 8
  },

  input: {
    height: 55,
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 15,
    fontSize: 18
  },

  button: {
    height: 55,
    backgroundColor: "#000000",
    borderRadius: 8,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 30
  },

  buttonText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "bold"
  },

  result: {
    marginTop: 35,
    padding: 20,
    borderWidth: 1,
    borderRadius: 10,
    alignItems: "center"
  },

  resultTitle: {
    fontSize: 18,
    fontWeight: "bold"
  },

  fare: {
    fontSize: 38,
    fontWeight: "bold",
    marginTop: 10,
    marginBottom: 20
  },

  breakdown: {
    width: "100%",
    gap: 8
  }

});
