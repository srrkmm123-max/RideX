import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert
} from "react-native";
import axios from "axios";

const API_URL = "http://localhost:8000";

export default function Login() {
  const [phone, setPhone] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (phone.length !== 10) {
      Alert.alert("Invalid Number", "Please enter a 10-digit mobile number.");
      return;
    }

    try {
      setLoading(true);

      const response = await axios.post(
        `${API_URL}/api/v1/users/login`,
        {
          phone: phone
        }
      );

      console.log("Login response:", response.data);

      Alert.alert(
        "Login Successful",
        "OTP has been sent to your mobile number."
      );

    } catch (error) {
      console.error("Login error:", error);

      Alert.alert(
        "Login Failed",
        "Unable to connect to the RideX server."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>

      <Text style={styles.logo}>RideX</Text>

      <Text style={styles.title}>
        Welcome to RideX
      </Text>

      <Text style={styles.subtitle}>
        Enter your mobile number to continue
      </Text>

      <TextInput
        style={styles.input}
        placeholder="Mobile Number"
        keyboardType="phone-pad"
        maxLength={10}
        value={phone}
        onChangeText={setPhone}
      />

      <TouchableOpacity
        style={styles.button}
        onPress={handleLogin}
        disabled={loading}
      >
        <Text style={styles.buttonText}>
          {loading ? "Sending..." : "Continue"}
        </Text>
      </TouchableOpacity>

    </View>
  );
}

const styles = StyleSheet.create({

  container: {
    flex: 1,
    justifyContent: "center",
    padding: 25,
    backgroundColor: "#ffffff"
  },

  logo: {
    fontSize: 42,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 30
  },

  title: {
    fontSize: 26,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 10
  },

  subtitle: {
    fontSize: 16,
    textAlign: "center",
    marginBottom: 30
  },

  input: {
    height: 55,
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 15,
    fontSize: 18,
    marginBottom: 20
  },

  button: {
    height: 55,
    borderRadius: 8,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#000000"
  },

  buttonText: {
    color: "#ffffff",
    fontSize: 18,
    fontWeight: "bold"
  }

});
