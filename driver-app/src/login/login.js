import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator
} from "react-native";
import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = "http://192.168.1.100:8000";

export default function Login() {

  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");

  const [otpSent, setOtpSent] =
    useState(false);

  const [loading, setLoading] =
    useState(false);


  // ==================================================
  // SEND OTP
  // ==================================================

  const sendOTP = async () => {

    if (phone.length !== 10) {

      Alert.alert(
        "Invalid Number",
        "Please enter a valid 10-digit mobile number."
      );

      return;
    }

    try {

      setLoading(true);

      const response = await axios.post(
        `${API_URL}/api/v1/drivers/send-otp`,
        {
          phone: phone
        }
      );

      console.log(
        "OTP response:",
        response.data
      );

      setOtpSent(true);

      Alert.alert(
        "OTP Sent",
        "OTP has been sent to your mobile number."
      );

    } catch (error) {

      console.error(
        "Send OTP error:",
        error
      );

      Alert.alert(
        "Error",
        "Unable to send OTP. Please try again."
      );

    } finally {

      setLoading(false);

    }
  };


  // ==================================================
  // VERIFY OTP
  // ==================================================

  const verifyOTP = async () => {

    if (otp.length !== 6) {

      Alert.alert(
        "Invalid OTP",
        "Please enter the 6-digit OTP."
      );

      return;
    }

    try {

      setLoading(true);

      const response = await axios.post(
        `${API_URL}/api/v1/drivers/verify-otp`,
        {
          phone: phone,
          otp: otp
        }
      );

      console.log(
        "Login response:",
        response.data
      );


      // Save authentication token
      if (response.data.access_token) {

        await AsyncStorage.setItem(
          "driver_token",
          response.data.access_token
        );

      }


      // Save driver ID
      if (response.data.driver_id) {

        await AsyncStorage.setItem(
          "driver_id",
          String(response.data.driver_id)
        );

      }


      Alert.alert(
        "Login Successful",
        "Welcome to RideX Driver!"
      );

    } catch (error) {

      console.error(
        "OTP verification error:",
        error
      );

      Alert.alert(
        "Login Failed",
        "Invalid or expired OTP."
      );

    } finally {

      setLoading(false);

    }
  };


  // ==================================================
  // SCREEN
  // ==================================================

  return (

    <View style={styles.container}>

      <Text style={styles.logo}>
        RideX
      </Text>

      <Text style={styles.driverLabel}>
        DRIVER
      </Text>

      <Text style={styles.title}>
        Welcome, Driver
      </Text>

      <Text style={styles.subtitle}>
        Login to start accepting rides
      </Text>


      {/* Phone */}

      <Text style={styles.label}>
        Mobile Number
      </Text>

      <TextInput

        style={styles.input}

        placeholder="10-digit mobile number"

        keyboardType="phone-pad"

        maxLength={10}

        value={phone}

        onChangeText={setPhone}

        editable={!otpSent}

      />


      {/* Send OTP */}

      {!otpSent && (

        <TouchableOpacity

          style={styles.button}

          onPress={sendOTP}

          disabled={loading}

        >

          {loading ? (

            <ActivityIndicator
              color="#ffffff"
            />

          ) : (

            <Text style={styles.buttonText}>
              Send OTP
            </Text>

          )}

        </TouchableOpacity>

      )}


      {/* OTP */}

      {otpSent && (

        <>

          <Text style={styles.label}>
            Enter OTP
          </Text>

          <TextInput

            style={styles.input}

            placeholder="6-digit OTP"

            keyboardType="number-pad"

            maxLength={6}

            value={otp}

            onChangeText={setOtp}

          />


          <TouchableOpacity

            style={styles.button}

            onPress={verifyOTP}

            disabled={loading}

          >

            {loading ? (

              <ActivityIndicator
                color="#ffffff"
              />

            ) : (

              <Text style={styles.buttonText}>
                Verify & Login
              </Text>

            )}

          </TouchableOpacity>


          {/* Change number */}

          <TouchableOpacity

            style={styles.changeButton}

            onPress={() => {

              setOtpSent(false);

              setOtp("");

            }}

          >

            <Text style={styles.changeText}>
              Change Mobile Number
            </Text>

          </TouchableOpacity>

        </>

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

    justifyContent: "center",

    padding: 25,

    backgroundColor: "#ffffff"

  },

  logo: {

    fontSize: 42,

    fontWeight: "bold",

    textAlign: "center",

    marginBottom: 5

  },

  driverLabel: {

    textAlign: "center",

    fontSize: 12,

    fontWeight: "bold",

    letterSpacing: 3,

    marginBottom: 30

  },

  title: {

    fontSize: 27,

    fontWeight: "bold",

    textAlign: "center",

    marginBottom: 10

  },

  subtitle: {

    fontSize: 16,

    textAlign: "center",

    marginBottom: 30

  },

  label: {

    fontSize: 16,

    fontWeight: "bold",

    marginBottom: 8,

    marginTop: 10

  },

  input: {

    height: 55,

    borderWidth: 1,

    borderRadius: 8,

    paddingHorizontal: 15,

    fontSize: 18,

    marginBottom: 15

  },

  button: {

    height: 55,

    borderRadius: 8,

    backgroundColor: "#000000",

    justifyContent: "center",

    alignItems: "center",

    marginTop: 10

  },

  buttonText: {

    color: "#ffffff",

    fontSize: 18,

    fontWeight: "bold"

  },

  changeButton: {

    alignItems: "center",

    marginTop: 20,

    padding: 10

  },

  changeText: {

    fontSize: 15,

    fontWeight: "600"

  }

});
