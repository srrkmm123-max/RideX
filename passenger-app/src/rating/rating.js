5import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  TextInput,
  StyleSheet,
  Alert,
  ActivityIndicator
} from "react-native";
import axios from "axios";

const API_URL = "http://192.168.1.100:8000";

const RIDE_ID = 1;

export default function Rating() {

  const [rating, setRating] = useState(0);

  const [comment, setComment] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  // ================================================
  // Submit rating
  // ================================================

  const submitRating = async () => {

    if (rating === 0) {

      Alert.alert(
        "Rating Required",
        "Please select a rating from 1 to 5 stars."
      );

      return;
    }

    try {

      setLoading(true);

      const ratingData = {

        ride_id: RIDE_ID,

        rating: rating,

        comment: comment.trim()

      };


      console.log(
        "Submitting rating:",
        ratingData
      );


      const response = await axios.post(

        `${API_URL}/api/v1/ratings`,

        ratingData

      );


      console.log(
        "Rating response:",
        response.data
      );


      Alert.alert(

        "Thank You! ⭐",

        "Your rating has been submitted successfully.",

        [
          {
            text: "OK",

            onPress: () => {

              setRating(0);

              setComment("");

            }

          }

        ]

      );

    } catch (error) {

      console.error(
        "Rating error:",
        error
      );

      Alert.alert(

        "Submission Failed",

        "Unable to submit your rating. Please try again."

      );

    } finally {

      setLoading(false);

    }

  };


  // ================================================
  // Star component
  // ================================================

  const Star = ({ number }) => {

    const selected =
      number <= rating;

    return (

      <TouchableOpacity

        onPress={() =>
          setRating(number)
        }

        style={styles.starButton}

      >

        <Text
          style={[
            styles.star,
            selected && styles.selectedStar
          ]}
        >

          ★

        </Text>

      </TouchableOpacity>

    );

  };


  // ================================================
  // Rating description
  // ================================================

  const getRatingText = () => {

    switch (rating) {

      case 1:
        return "Very Poor";

      case 2:
        return "Poor";

      case 3:
        return "Average";

      case 4:
        return "Good";

      case 5:
        return "Excellent";

      default:
        return "Tap a star to rate";

    }

  };


  // ================================================
  // Screen
  // ================================================

  return (

    <View style={styles.container}>


      <Text style={styles.title}>
        Rate Your Ride
      </Text>


      <Text style={styles.subtitle}>
        How was your experience with your driver?
      </Text>


      {/* Driver */}

      <View style={styles.driverCard}>

        <View style={styles.avatar}>

          <Text style={styles.avatarText}>
            R
          </Text>

        </View>


        <View>

          <Text style={styles.driverName}>
            Ravi
          </Text>

          <Text style={styles.vehicle}>
            🏍️ TS09 AB1234
          </Text>

        </View>

      </View>


      {/* Stars */}

      <View style={styles.starsContainer}>

        <Star number={1} />

        <Star number={2} />

        <Star number={3} />

        <Star number={4} />

        <Star number={5} />

      </View>


      {/* Rating description */}

      <Text style={styles.ratingText}>

        {getRatingText()}

      </Text>


      {/* Comment */}

      <TextInput

        style={styles.commentInput}

        placeholder="Tell us about your experience (optional)"

        multiline

        numberOfLines={5}

        value={comment}

        onChangeText={setComment}

        textAlignVertical="top"

        maxLength={500}

      />


      <Text style={styles.characterCount}>

        {comment.length}/500

      </Text>


      {/* Submit */}

      <TouchableOpacity

        style={[
          styles.submitButton,
          rating === 0 &&
            styles.disabledButton
        ]}

        onPress={submitRating}

        disabled={
          rating === 0 || loading
        }

      >

        {loading ? (

          <ActivityIndicator
            color="#ffffff"
          />

        ) : (

          <Text style={styles.submitText}>
            Submit Rating
          </Text>

        )}

      </TouchableOpacity>


      {/* Skip */}

      <TouchableOpacity

        style={styles.skipButton}

        onPress={() => {

          Alert.alert(
            "Rating Skipped",
            "You can rate your ride later."
          );

        }}

      >

        <Text style={styles.skipText}>
          Skip
        </Text>

      </TouchableOpacity>

    </View>

  );

}


// ==================================================
// Styles
// ==================================================

const styles = StyleSheet.create({

  container: {

    flex: 1,

    padding: 25,

    backgroundColor: "#ffffff",

    alignItems: "center"

  },

  title: {

    fontSize: 28,

    fontWeight: "bold",

    marginTop: 50,

    textAlign: "center"

  },

  subtitle: {

    fontSize: 16,

    textAlign: "center",

    marginTop: 10,

    marginBottom: 30

  },

  driverCard: {

    width: "100%",

    padding: 18,

    borderWidth: 1,

    borderRadius: 10,

    flexDirection: "row",

    alignItems: "center"

  },

  avatar: {

    width: 55,

    height: 55,

    borderRadius: 28,

    backgroundColor: "#eeeeee",

    justifyContent: "center",

    alignItems: "center",

    marginRight: 15

  },

  avatarText: {

    fontSize: 25,

    fontWeight: "bold"

  },

  driverName: {

    fontSize: 19,

    fontWeight: "bold"

  },

  vehicle: {

    fontSize: 14,

    marginTop: 5

  },

  starsContainer: {

    flexDirection: "row",

    marginTop: 35,

    marginBottom: 10

  },

  starButton: {

    paddingHorizontal: 5

  },

  star: {

    fontSize: 48,

    color: "#cccccc"

  },

  selectedStar: {

    color: "#f5b400"

  },

  ratingText: {

    fontSize: 18,

    fontWeight: "600",

    marginBottom: 25

  },

  commentInput: {

    width: "100%",

    minHeight: 120,

    borderWidth: 1,

    borderRadius: 10,

    padding: 15,

    fontSize: 16

  },

  characterCount: {

    alignSelf: "flex-end",

    marginTop: 5,

    fontSize: 12

  },

  submitButton: {

    width: "100%",

    height: 55,

    backgroundColor: "#000000",

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center",

    marginTop: 25

  },

  disabledButton: {

    opacity: 0.4

  },

  submitText: {

    color: "#ffffff",

    fontSize: 18,

    fontWeight: "bold"

  },

  skipButton: {

    marginTop: 15,

    padding: 10

  },

  skipText: {

    fontSize: 16,

    fontWeight: "600"

  }

});
