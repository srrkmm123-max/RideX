import React, { useCallback, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  FlatList,
  RefreshControl,
  Alert,
  ActivityIndicator
} from "react-native";

import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = "http://192.168.1.100:8000";

export default function Earnings() {

  const [earnings, setEarnings] = useState({
    today: 0,
    week: 0,
    month: 0,
    total: 0,
    tripsToday: 0,
    tripsWeek: 0,
    tripsMonth: 0
  });

  const [rides, setRides] = useState([]);

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [selectedPeriod, setSelectedPeriod] =
    useState("today");


  // ==================================================
  // GET DRIVER TOKEN
  // ==================================================

  const getToken = async () => {

    return await AsyncStorage.getItem(
      "driver_token"
    );

  };


  // ==================================================
  // GET DRIVER ID
  // ==================================================

  const getDriverId = async () => {

    return await AsyncStorage.getItem(
      "driver_id"
    );

  };


  // ==================================================
  // LOAD EARNINGS
  // ==================================================

  const loadEarnings = useCallback(
    async () => {

      try {

        const token =
          await getToken();

        const driverId =
          await getDriverId();


        if (!token || !driverId) {

          Alert.alert(
            "Login Required",
            "Please login as a driver."
          );

          setLoading(false);

          return;

        }


        // ------------------------------------------
        // Earnings summary
        // ------------------------------------------

        const earningsResponse =
          await fetch(

            `${API_URL}/api/v1/drivers/${driverId}/earnings`,

            {

              method: "GET",

              headers: {

                "Authorization":
                  `Bearer ${token}`,

                "Content-Type":
                  "application/json"

              }

            }

          );


        if (!earningsResponse.ok) {

          throw new Error(
            "Unable to load earnings"
          );

        }


        const earningsData =
          await earningsResponse.json();


        setEarnings({

          today:
            earningsData.today || 0,

          week:
            earningsData.week || 0,

          month:
            earningsData.month || 0,

          total:
            earningsData.total || 0,

          tripsToday:
            earningsData.trips_today || 0,

          tripsWeek:
            earningsData.trips_week || 0,

          tripsMonth:
            earningsData.trips_month || 0

        });


        // ------------------------------------------
        // Completed rides
        // ------------------------------------------

        const ridesResponse =
          await fetch(

            `${API_URL}/api/v1/drivers/${driverId}/earnings/rides`,

            {

              method: "GET",

              headers: {

                "Authorization":
                  `Bearer ${token}`,

                "Content-Type":
                  "application/json"

              }

            }

          );


        if (ridesResponse.ok) {

          const ridesData =
            await ridesResponse.json();


          setRides(
            ridesData.rides || []
          );

        }

      } catch (error) {

        console.error(
          "Earnings error:",
          error
        );


        Alert.alert(
          "Error",
          "Unable to load earnings."
        );

      } finally {

        setLoading(false);

        setRefreshing(false);

      }

    },
    []
  );


  // ==================================================
  // INITIAL LOAD
  // ==================================================

  React.useEffect(() => {

    loadEarnings();

  }, [loadEarnings]);


  // ==================================================
  // REFRESH
  // ==================================================

  const onRefresh = () => {

    setRefreshing(true);

    loadEarnings();

  };


  // ==================================================
  // PERIOD DATA
  // ==================================================

  const getPeriodData = () => {

    switch (selectedPeriod) {

      case "week":

        return {

          amount:
            earnings.week,

          trips:
            earnings.tripsWeek

        };


      case "month":

        return {

          amount:
            earnings.month,

          trips:
            earnings.tripsMonth

        };


      default:

        return {

          amount:
            earnings.today,

          trips:
            earnings.tripsToday

        };

    }

  };


  const period =
    getPeriodData();


  // ==================================================
  // FORMAT MONEY
  // ==================================================

  const formatMoney = amount => {

    return `₹${Number(amount || 0).toLocaleString(
      "en-IN"
    )}`;

  };


  // ==================================================
  // RIDE ITEM
  // ==================================================

  const renderRide =
    ({ item }) => (

      <View style={styles.rideCard}>

        <View style={styles.rideLeft}>

          <Text style={styles.rideId}>

            Ride #{item.ride_id}

          </Text>


          <Text style={styles.rideDate}>

            {item.date || "Date unavailable"}

          </Text>


          <Text style={styles.rideRoute}>

            {item.pickup || "Pickup"}

          </Text>


          <Text style={styles.arrow}>
            ↓
          </Text>


          <Text style={styles.rideRoute}>

            {item.drop || "Destination"}

          </Text>

        </View>


        <View style={styles.rideRight}>

          <Text style={styles.rideAmount}>

            {formatMoney(item.driver_earnings)}

          </Text>


          <Text style={styles.completed}>

            Completed

          </Text>


          {item.distance && (

            <Text style={styles.distance}>

              {item.distance} km

            </Text>

          )}

        </View>

      </View>

    );


  // ==================================================
  // LOADING
  // ==================================================

  if (loading) {

    return (

      <View style={styles.center}>

        <ActivityIndicator
          size="large"
        />

        <Text style={styles.loadingText}>

          Loading earnings...

        </Text>

      </View>

    );

  }


  // ==================================================
  // SCREEN
  // ==================================================

  return (

    <View style={styles.container}>


      <FlatList

        data={rides}

        keyExtractor={item =>
          String(item.ride_id)
        }

        renderItem={renderRide}

        refreshControl={

          <RefreshControl

            refreshing={refreshing}

            onRefresh={onRefresh}

          />

        }

        ListHeaderComponent={

          <>

            {/* Header */}

            <View style={styles.header}>

              <Text style={styles.title}>

                Earnings

              </Text>


              <TouchableOpacity
                onPress={onRefresh}
              >

                <Text style={styles.refreshText}>

                  ↻

                </Text>

              </TouchableOpacity>

            </View>


            {/* Main earnings */}

            <View style={styles.mainCard}>

              <Text style={styles.mainLabel}>

                {selectedPeriod === "today"
                  ? "Today's Earnings"
                  : selectedPeriod === "week"
                    ? "This Week"
                    : "This Month"}

              </Text>


              <Text style={styles.mainAmount}>

                {formatMoney(
                  period.amount
                )}

              </Text>


              <Text style={styles.tripCount}>

                {period.trips} completed rides

              </Text>

            </View>


            {/* Period selector */}

            <View style={styles.periodContainer}>


              <TouchableOpacity

                style={[
                  styles.periodButton,

                  selectedPeriod === "today" &&
                    styles.selectedPeriod
                ]}

                onPress={() =>
                  setSelectedPeriod(
                    "today"
                  )
                }

              >

                <Text
                  style={[
                    styles.periodText,

                    selectedPeriod === "today" &&
                      styles.selectedPeriodText
                  ]}
                >

                  Today

                </Text>

              </TouchableOpacity>


              <TouchableOpacity

                style={[
                  styles.periodButton,

                  selectedPeriod === "week" &&
                    styles.selectedPeriod
                ]}

                onPress={() =>
                  setSelectedPeriod(
                    "week"
                  )
                }

              >

                <Text
                  style={[
                    styles.periodText,

                    selectedPeriod === "week" &&
                      styles.selectedPeriodText
                  ]}
                >

                  Week

                </Text>

              </TouchableOpacity>


              <TouchableOpacity

                style={[
                  styles.periodButton,

                  selectedPeriod === "month" &&
                    styles.selectedPeriod
                ]}

                onPress={() =>
                  setSelectedPeriod(
                    "month"
                  )
                }

              >

                <Text
                  style={[
                    styles.periodText,

                    selectedPeriod === "month" &&
                      styles.selectedPeriodText
                  ]}
                >

                  Month

                </Text>

              </TouchableOpacity>


            </View>


            {/* Statistics */}

            <View style={styles.statsContainer}>


              <View style={styles.statCard}>

                <Text style={styles.statLabel}>

                  Today

                </Text>

                <Text style={styles.statAmount}>

                  {formatMoney(
                    earnings.today
                  )}

                </Text>

                <Text style={styles.statTrips}>

                  {earnings.tripsToday} trips

                </Text>

              </View>


              <View style={styles.statCard}>

                <Text style={styles.statLabel}>

                  This Week

                </Text>

                <Text style={styles.statAmount}>

                  {formatMoney(
                    earnings.week
                  )}

                </Text>

                <Text style={styles.statTrips}>

                  {earnings.tripsWeek} trips

                </Text>

              </View>


              <View style={styles.statCard}>

                <Text style={styles.statLabel}>

                  This Month

                </Text>

                <Text style={styles.statAmount}>

                  {formatMoney(
                    earnings.month
                  )}

                </Text>

                <Text style={styles.statTrips}>

                  {earnings.tripsMonth} trips

                </Text>

              </View>


            </View>


            {/* Total */}

            <View style={styles.totalCard}>

              <Text style={styles.totalLabel}>

                Lifetime Earnings

              </Text>


              <Text style={styles.totalAmount}>

                {formatMoney(
                  earnings.total
                )}

              </Text>

            </View>


            {/* Ride history */}

            <Text style={styles.historyTitle}>

              Recent Completed Rides

            </Text>


          </>

        }

        ListEmptyComponent={

          <View style={styles.empty}>

            <Text style={styles.emptyTitle}>

              No completed rides

            </Text>


            <Text style={styles.emptyText}>

              Your completed rides will
              appear here.

            </Text>

          </View>

        }

        ListFooterComponent={

          rides.length > 0 ? (

            <TouchableOpacity
              style={styles.loadMoreButton}
              onPress={() =>
                Alert.alert(
                  "RideX",
                  "Load-more pagination can be implemented here."
                )
              }
            >

              <Text style={styles.loadMoreText}>

                View More

              </Text>

            </TouchableOpacity>

          ) : null

        }

      />

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

  center: {

    flex: 1,

    justifyContent: "center",

    alignItems: "center"

  },

  loadingText: {

    marginTop: 15,

    fontSize: 16

  },

  header: {

    flexDirection: "row",

    justifyContent: "space-between",

    alignItems: "center",

    paddingHorizontal: 20,

    paddingTop: 25,

    paddingBottom: 15

  },

  title: {

    fontSize: 28,

    fontWeight: "bold"

  },

  refreshText: {

    fontSize: 30,

    fontWeight: "bold"

  },

  mainCard: {

    marginHorizontal: 20,

    padding: 25,

    borderWidth: 1,

    borderRadius: 14,

    alignItems: "center"

  },

  mainLabel: {

    fontSize: 15,

    marginBottom: 10

  },

  mainAmount: {

    fontSize: 38,

    fontWeight: "bold"

  },

  tripCount: {

    marginTop: 8,

    fontSize: 14

  },

  periodContainer: {

    flexDirection: "row",

    marginHorizontal: 20,

    marginTop: 15,

    borderWidth: 1,

    borderRadius: 10,

    overflow: "hidden"

  },

  periodButton: {

    flex: 1,

    paddingVertical: 12,

    alignItems: "center"

  },

  selectedPeriod: {

    backgroundColor: "#000000"

  },

  periodText: {

    fontSize: 14,

    fontWeight: "bold"

  },

  selectedPeriodText: {

    color: "#ffffff"

  },

  statsContainer: {

    flexDirection: "row",

    marginHorizontal: 20,

    marginTop: 15,

    gap: 8

  },

  statCard: {

    flex: 1,

    padding: 12,

    borderWidth: 1,

    borderRadius: 10

  },

  statLabel: {

    fontSize: 12,

    marginBottom: 6

  },

  statAmount: {

    fontSize: 16,

    fontWeight: "bold"

  },

  statTrips: {

    fontSize: 11,

    marginTop: 4

  },

  totalCard: {

    marginHorizontal: 20,

    marginTop: 15,

    padding: 18,

    borderWidth: 1,

    borderRadius: 10,

    flexDirection: "row",

    justifyContent: "space-between",

    alignItems: "center"

  },

  totalLabel: {

    fontSize: 15,

    fontWeight: "bold"

  },

  totalAmount: {

    fontSize: 20,

    fontWeight: "bold"

  },

  historyTitle: {

    fontSize: 20,

    fontWeight: "bold",

    marginHorizontal: 20,

    marginTop: 25,

    marginBottom: 10

  },

  rideCard: {

    marginHorizontal: 20,

    marginVertical: 6,

    padding: 15,

    borderWidth: 1,

    borderRadius: 10,

    flexDirection: "row",

    justifyContent: "space-between"

  },

  rideLeft: {

    flex: 1,

    paddingRight: 10

  },

  rideRight: {

    alignItems: "flex-end",

    justifyContent: "flex-start"

  },

  rideId: {

    fontSize: 15,

    fontWeight: "bold"

  },

  rideDate: {

    fontSize: 12,

    marginTop: 3

  },

  rideRoute: {

    fontSize: 13,

    marginTop: 8

  },

  arrow: {

    fontSize: 12,

    marginTop: 2

  },

  rideAmount: {

    fontSize: 18,

    fontWeight: "bold"

  },

  completed: {

    fontSize: 11,

    marginTop: 5

  },

  distance: {

    fontSize: 11,

    marginTop: 5

  },

  empty: {

    alignItems: "center",

    padding: 30

  },

  emptyTitle: {

    fontSize: 18,

    fontWeight: "bold"

  },

  emptyText: {

    marginTop: 8,

    fontSize: 14

  },

  loadMoreButton: {

    margin: 20,

    height: 50,

    borderWidth: 1,

    borderRadius: 8,

    justifyContent: "center",

    alignItems: "center"

  },

  loadMoreText: {

    fontSize: 16,

    fontWeight: "bold"

  }

});
