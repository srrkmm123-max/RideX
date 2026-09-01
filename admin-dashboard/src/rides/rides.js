import React, { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000/api/v1";

export default function Rides() {
  const [rides, setRides] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [rideTypeFilter, setRideTypeFilter] = useState("all");

  const [selectedRide, setSelectedRide] = useState(null);

  // ==================================================
  // AUTH
  // ==================================================

  const getToken = () => {
    return localStorage.getItem("admin_token");
  };

  const getConfig = () => {
    const token = getToken();

    return {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    };
  };

  // ==================================================
  // LOAD RIDES
  // ==================================================

  const loadRides = useCallback(async () => {
    try {
      setError("");

      const response = await axios.get(
        `${API_URL}/admin/rides`,
        getConfig()
      );

      setRides(response.data.rides || []);
    } catch (err) {
      console.error("Load rides error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to load rides."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadRides();
  }, [loadRides]);

  // ==================================================
  // REFRESH
  // ==================================================

  const refreshRides = () => {
    setRefreshing(true);
    loadRides();
  };

  // ==================================================
  // FILTER
  // ==================================================

  const filteredRides = useMemo(() => {
    const searchText = search
      .toLowerCase()
      .trim();

    return rides.filter((ride) => {
      const matchesSearch =
        !searchText ||
        String(ride.id || "")
          .toLowerCase()
          .includes(searchText) ||
        String(ride.passenger_name || "")
          .toLowerCase()
          .includes(searchText) ||
        String(ride.driver_name || "")
          .toLowerCase()
          .includes(searchText) ||
        String(ride.passenger_phone || "")
          .toLowerCase()
          .includes(searchText) ||
        String(ride.driver_phone || "")
          .toLowerCase()
          .includes(searchText) ||
        String(ride.pickup_address || "")
          .toLowerCase()
          .includes(searchText) ||
        String(ride.drop_address || "")
          .toLowerCase()
          .includes(searchText);

      const matchesStatus =
        statusFilter === "all" ||
        ride.status === statusFilter;

      const matchesType =
        rideTypeFilter === "all" ||
        ride.ride_type === rideTypeFilter;

      return (
        matchesSearch &&
        matchesStatus &&
        matchesType
      );
    });
  }, [
    rides,
    search,
    statusFilter,
    rideTypeFilter
  ]);

  // ==================================================
  // VIEW RIDE
  // ==================================================

  const viewRide = async (ride) => {
    try {
      const response = await axios.get(
        `${API_URL}/admin/rides/${ride.id}`,
        getConfig()
      );

      setSelectedRide(response.data);
    } catch (err) {
      console.error(
        "View ride error:",
        err
      );

      setSelectedRide(ride);
    }
  };

  // ==================================================
  // UPDATE RIDE STATUS
  // ==================================================

  const updateRideStatus = async (
    ride,
    newStatus
  ) => {
    try {
      await axios.patch(
        `${API_URL}/admin/rides/${ride.id}/status`,
        {
          status: newStatus
        },
        getConfig()
      );

      setRides((previousRides) =>
        previousRides.map((currentRide) =>
          currentRide.id === ride.id
            ? {
                ...currentRide,
                status: newStatus
              }
            : currentRide
        )
      );

      if (
        selectedRide?.id === ride.id
      ) {
        setSelectedRide({
          ...selectedRide,
          status: newStatus
        });
      }
    } catch (err) {
      console.error(
        "Update ride status error:",
        err
      );

      alert(
        err.response?.data?.detail ||
          "Unable to update ride status."
      );
    }
  };

  // ==================================================
  // CANCEL RIDE
  // ==================================================

  const cancelRide = async (ride) => {
    const confirmed = window.confirm(
      `Cancel ride #${ride.id}?`
    );

    if (!confirmed) {
      return;
    }

    try {
      await axios.post(
        `${API_URL}/admin/rides/${ride.id}/cancel`,
        {
          reason:
            "Cancelled by administrator"
        },
        getConfig()
      );

      setRides((previousRides) =>
        previousRides.map((currentRide) =>
          currentRide.id === ride.id
            ? {
                ...currentRide,
                status: "cancelled"
              }
            : currentRide
        )
      );

      if (
        selectedRide?.id === ride.id
      ) {
        setSelectedRide({
          ...selectedRide,
          status: "cancelled"
        });
      }
    } catch (err) {
      console.error(
        "Cancel ride error:",
        err
      );

      alert(
        err.response?.data?.detail ||
          "Unable to cancel ride."
      );
    }
  };

  // ==================================================
  // EXPORT CSV
  // ==================================================

  const exportRides = () => {
    if (filteredRides.length === 0) {
      alert("No rides to export.");
      return;
    }

    const headers = [
      "Ride ID",
      "Passenger",
      "Passenger Phone",
      "Driver",
      "Driver Phone",
      "Ride Type",
      "Status",
      "Pickup",
      "Drop",
      "Fare",
      "Distance KM",
      "Payment Status",
      "Requested At",
      "Completed At"
    ];

    const rows = filteredRides.map(
      (ride) => [
        ride.id || "",
        ride.passenger_name || "",
        ride.passenger_phone || "",
        ride.driver_name || "",
        ride.driver_phone || "",
        ride.ride_type || "",
        ride.status || "",
        ride.pickup_address || "",
        ride.drop_address || "",
        ride.final_fare ??
          ride.estimated_fare ??
          "",
        ride.distance_km || "",
        ride.payment_status || "",
        ride.requested_at || "",
        ride.completed_at || ""
      ]
    );

    const csv = [headers, ...rows]
      .map((row) =>
        row
          .map(
            (value) =>
              `"${String(value).replace(
                /"/g,
                '""'
              )}"`
          )
          .join(",")
      )
      .join("\n");

    const blob = new Blob([csv], {
      type: "text/csv;charset=utf-8;"
    });

    const url =
      URL.createObjectURL(blob);

    const link =
      document.createElement("a");

    link.href = url;
    link.download =
      "ridex-rides.csv";

    link.click();

    URL.revokeObjectURL(url);
  };

  // ==================================================
  // STATISTICS
  // ==================================================

  const totalRides = rides.length;

  const requestedRides = rides.filter(
    (ride) =>
      ride.status === "requested"
  ).length;

  const searchingRides = rides.filter(
    (ride) =>
      ride.status === "searching_driver"
  ).length;

  const acceptedRides = rides.filter(
    (ride) =>
      ride.status === "accepted"
  ).length;

  const ongoingRides = rides.filter(
    (ride) =>
      ride.status === "driver_arriving" ||
      ride.status === "driver_arrived" ||
      ride.status === "in_progress"
  ).length;

  const completedRides = rides.filter(
    (ride) =>
      ride.status === "completed"
  ).length;

  const cancelledRides = rides.filter(
    (ride) =>
      ride.status === "cancelled"
  ).length;

  const totalRevenue = rides.reduce(
    (sum, ride) => {
      if (ride.status !== "completed") {
        return sum;
      }

      return (
        sum +
        Number(
          ride.final_fare ??
            ride.estimated_fare ??
            0
        )
      );
    },
    0
  );

  // ==================================================
  // LOADING
  // ==================================================

  if (loading) {
    return (
      <div style={styles.center}>
        <div style={styles.loading}>
          Loading rides...
        </div>
      </div>
    );
  }

  // ==================================================
  // SCREEN
  // ==================================================

  return (
    <div style={styles.page}>

      {/* HEADER */}

      <div style={styles.header}>

        <div>
          <h1 style={styles.title}>
            Rides
          </h1>

          <p style={styles.subtitle}>
            Monitor and manage all RideX trips
          </p>
        </div>

        <div style={styles.headerButtons}>

          <button
            style={styles.secondaryButton}
            onClick={refreshRides}
            disabled={refreshing}
          >
            {refreshing
              ? "Refreshing..."
              : "↻ Refresh"}
          </button>

          <button
            style={styles.primaryButton}
            onClick={exportRides}
          >
            Export CSV
          </button>

        </div>

      </div>

      {/* ERROR */}

      {error && (
        <div style={styles.error}>
          {error}
        </div>
      )}

      {/* STATISTICS */}

      <div style={styles.statsGrid}>

        <StatCard
          title="Total Rides"
          value={totalRides}
        />

        <StatCard
          title="Requested"
          value={requestedRides}
        />

        <StatCard
          title="Finding Driver"
          value={searchingRides}
        />

        <StatCard
          title="Accepted"
          value={acceptedRides}
        />

        <StatCard
          title="Ongoing"
          value={ongoingRides}
        />

        <StatCard
          title="Completed"
          value={completedRides}
        />

        <StatCard
          title="Cancelled"
          value={cancelledRides}
        />

        <StatCard
          title="Revenue"
          value={`₹${totalRevenue.toFixed(2)}`}
        />

      </div>

      {/* FILTERS */}

      <div style={styles.filterCard}>

        <input
          type="text"
          placeholder="Search ride, passenger, driver or location..."
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
          style={styles.searchInput}
        />

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(
              event.target.value
            )
          }
          style={styles.select}
        >
          <option value="all">
            All Status
          </option>

          <option value="requested">
            Requested
          </option>

          <option value="searching_driver">
            Finding Driver
          </option>

          <option value="accepted">
            Accepted
          </option>

          <option value="driver_arriving">
            Driver Arriving
          </option>

          <option value="driver_arrived">
            Driver Arrived
          </option>

          <option value="in_progress">
            In Progress
          </option>

          <option value="completed">
            Completed
          </option>

          <option value="cancelled">
            Cancelled
          </option>
        </select>

        <select
          value={rideTypeFilter}
          onChange={(event) =>
            setRideTypeFilter(
              event.target.value
            )
          }
          style={styles.select}
        >
          <option value="all">
            All Ride Types
          </option>

          <option value="economy">
            Economy
          </option>

          <option value="premium">
            Premium
          </option>

          <option value="xl">
            XL
          </option>

          <option value="bike">
            Bike
          </option>

          <option value="auto">
            Auto
          </option>
        </select>

      </div>

      {/* RIDE TABLE */}

      <div style={styles.tableCard}>

        <table style={styles.table}>

          <thead>
            <tr>

              <th style={styles.th}>
                Ride
              </th>

              <th style={styles.th}>
                Passenger
              </th>

              <th style={styles.th}>
                Driver
              </th>

              <th style={styles.th}>
                Route
              </th>

              <th style={styles.th}>
                Type
              </th>

              <th style={styles.th}>
                Status
              </th>

              <th style={styles.th}>
                Fare
              </th>

              <th style={styles.th}>
                Payment
              </th>

              <th style={styles.th}>
                Actions
              </th>

            </tr>
          </thead>

          <tbody>

            {filteredRides.map(
              (ride) => (

                <tr key={ride.id}>

                  {/* RIDE */}

                  <td style={styles.td}>

                    <div style={styles.rideId}>
                      #{ride.id}
                    </div>

                    <div style={styles.rideDate}>
                      {formatDate(
                        ride.requested_at
                      )}
                    </div>

                  </td>

                  {/* PASSENGER */}

                  <td style={styles.td}>

                    <div style={styles.name}>
                      {ride.passenger_name ||
                        "Unassigned"}
                    </div>

                    <div style={styles.smallText}>
                      {ride.passenger_phone ||
                        "-"}
                    </div>

                  </td>

                  {/* DRIVER */}

                  <td style={styles.td}>

                    <div style={styles.name}>
                      {ride.driver_name ||
                        "Not assigned"}
                    </div>

                    <div style={styles.smallText}>
                      {ride.driver_phone ||
                        "-"}
                    </div>

                  </td>

                  {/* ROUTE */}

                  <td style={styles.routeCell}>

                    <div>
                      <span style={styles.pickupDot}>
                        ●
                      </span>

                      {ride.pickup_address ||
                        "-"}
                    </div>

                    <div style={styles.routeLine}>
                      │
                    </div>

                    <div>
                      <span style={styles.dropDot}>
                        ●
                      </span>

                      {ride.drop_address ||
                        "-"}
                    </div>

                  </td>

                  {/* TYPE */}

                  <td style={styles.td}>
                    <RideTypeBadge
                      type={ride.ride_type}
                    />
                  </td>

                  {/* STATUS */}

                  <td style={styles.td}>
                    <RideStatusBadge
                      status={ride.status}
                    />
                  </td>

                  {/* FARE */}

                  <td style={styles.td}>

                    <div style={styles.fare}>
                      ₹
                      {Number(
                        ride.final_fare ??
                          ride.estimated_fare ??
                          0
                      ).toFixed(2)}
                    </div>

                  </td>

                  {/* PAYMENT */}

                  <td style={styles.td}>

                    <PaymentBadge
                      status={
                        ride.payment_status
                      }
                    />

                  </td>

                  {/* ACTIONS */}

                  <td style={styles.td}>

                    <div style={styles.actions}>

                      <button
                        style={styles.viewButton}
                        onClick={() =>
                          viewRide(ride)
                        }
                      >
                        View
                      </button>

                      {[
                        "requested",
                        "searching_driver",
                        "accepted",
                        "driver_arriving",
                        "driver_arrived",
                        "in_progress"
                      ].includes(
                        ride.status
                      ) && (

                        <button
                          style={
                            styles.cancelButton
                          }
                          onClick={() =>
                            cancelRide(ride)
                          }
                        >
                          Cancel
                        </button>

                      )}

                    </div>

                  </td>

                </tr>

              )
            )}

          </tbody>

        </table>

        {filteredRides.length === 0 && (
          <div style={styles.empty}>

            <h3>
              No rides found
            </h3>

            <p>
              Try changing your search
              or filters.
            </p>

          </div>
        )}

      </div>

      {/* RIDE DETAILS MODAL */}

      {selectedRide && (

        <div style={styles.modalOverlay}>

          <div style={styles.modal}>

            <div style={styles.modalHeader}>

              <div>
                <h2 style={{ margin: 0 }}>
                  Ride #{selectedRide.id}
                </h2>

                <div style={styles.modalSubtitle}>
                  Ride details
                </div>
              </div>

              <button
                style={styles.closeButton}
                onClick={() =>
                  setSelectedRide(null)
                }
              >
                ×
              </button>

            </div>

            <div style={styles.modalBody}>

              <SectionTitle title="Ride Information" />

              <DetailRow
                label="Ride ID"
                value={`#${selectedRide.id}`}
              />

              <DetailRow
                label="Status"
                value={
                  selectedRide.status
                }
              />

              <DetailRow
                label="Ride Type"
                value={
                  selectedRide.ride_type
                }
              />

              <DetailRow
                label="Distance"
                value={
                  selectedRide.distance_km
                    ? `${selectedRide.distance_km} km`
                    : "-"
                }
              />

              <DetailRow
                label="Estimated Duration"
                value={
                  selectedRide.duration_minutes
                    ? `${selectedRide.duration_minutes} min`
                    : "-"
                }
              />

              <SectionTitle title="Passenger" />

              <DetailRow
                label="Name"
                value={
                  selectedRide.passenger_name
                }
              />

              <DetailRow
                label="Phone"
                value={
                  selectedRide.passenger_phone
                }
              />

              <SectionTitle title="Driver" />

              <DetailRow
                label="Name"
                value={
                  selectedRide.driver_name
                }
              />

              <DetailRow
                label="Phone"
                value={
                  selectedRide.driver_phone
                }
              />

              <SectionTitle title="Route" />

              <DetailRow
                label="Pickup"
                value={
                  selectedRide.pickup_address
                }
              />

              <DetailRow
                label="Drop"
                value={
                  selectedRide.drop_address
                }
              />

              <SectionTitle title="Payment" />

              <DetailRow
                label="Estimated Fare"
                value={
                  selectedRide.estimated_fare
                    ? `₹${Number(
                        selectedRide.estimated_fare
                      ).toFixed(2)}`
                    : "-"
                }
              />

              <DetailRow
                label="Final Fare"
                value={
                  selectedRide.final_fare
                    ? `₹${Number(
                        selectedRide.final_fare
                      ).toFixed(2)}`
                    : "-"
                }
              />

              <DetailRow
                label="Payment Method"
                value={
                  selectedRide.payment_method
                }
              />

              <DetailRow
                label="Payment Status"
                value={
                  selectedRide.payment_status
                }
              />

              <SectionTitle title="Time" />

              <DetailRow
                label="Requested"
                value={
                  selectedRide.requested_at
                }
              />

              <DetailRow
                label="Accepted"
                value={
                  selectedRide.accepted_at
                }
              />

              <DetailRow
                label="Started"
                value={
                  selectedRide.started_at
                }
              />

              <DetailRow
                label="Completed"
                value={
                  selectedRide.completed_at
                }
              />

              <DetailRow
                label="Cancelled"
                value={
                  selectedRide.cancelled_at
                }
              />

              <DetailRow
                label="Cancellation Reason"
                value={
                  selectedRide.cancellation_reason
                }
              />

            </div>

            <div style={styles.modalFooter}>

              {[
                "requested",
                "searching_driver",
                "accepted",
                "driver_arriving",
                "driver_arrived",
                "in_progress"
              ].includes(
                selectedRide.status
              ) && (

                <button
                  style={
                    styles.cancelButtonLarge
                  }
                  onClick={() =>
                    cancelRide(
                      selectedRide
                    )
                  }
                >
                  Cancel Ride
                </button>

              )}

              <button
                style={styles.closeModalButton}
                onClick={() =>
                  setSelectedRide(null)
                }
              >
                Close
              </button>

            </div>

          </div>

        </div>

      )}

    </div>
  );
}


// ==================================================
// STAT CARD
// ==================================================

function StatCard({ title, value }) {
  return (
    <div style={styles.statCard}>

      <div style={styles.statTitle}>
        {title}
      </div>

      <div style={styles.statValue}>
        {value}
      </div>

    </div>
  );
}


// ==================================================
// RIDE STATUS
// ==================================================

function RideStatusBadge({ status }) {
  const value = status || "unknown";

  return (
    <span
      style={{
        ...styles.badge,

        ...(value === "completed"
          ? styles.completedBadge
          : value === "cancelled"
          ? styles.cancelledBadge
          : value === "in_progress"
          ? styles.inProgressBadge
          : value === "accepted"
          ? styles.acceptedBadge
          : value === "requested"
          ? styles.requestedBadge
          : styles.defaultBadge)
      }}
    >
      {formatStatus(value)}
    </span>
  );
}


// ==================================================
// RIDE TYPE
// ==================================================

function RideTypeBadge({ type }) {
  return (
    <span style={styles.typeBadge}>
      {formatStatus(type || "standard")}
    </span>
  );
}


// ==================================================
// PAYMENT
// ==================================================

function PaymentBadge({ status }) {
  const value = status || "unknown";

  return (
    <span
      style={{
        ...styles.paymentBadge,

        ...(value === "paid"
          ? styles.paidBadge
          : value === "failed"
          ? styles.failedBadge
          : styles.pendingPaymentBadge)
      }}
    >
      {formatStatus(value)}
    </span>
  );
}


// ==================================================
// SECTION TITLE
// ==================================================

function SectionTitle({ title }) {
  return (
    <h3 style={styles.sectionTitle}>
      {title}
    </h3>
  );
}


// ==================================================
// DETAIL ROW
// ==================================================

function DetailRow({ label, value }) {
  return (
    <div style={styles.detailRow}>

      <span style={styles.detailLabel}>
        {label}
      </span>

      <span style={styles.detailValue}>
        {value || "-"}
      </span>

    </div>
  );
}


// ==================================================
// FORMAT STATUS
// ==================================================

function formatStatus(value) {
  if (!value) {
    return "-";
  }

  return String(value)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}


// ==================================================
// FORMAT DATE
// ==================================================

function formatDate(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}


// ==================================================
// STYLES
// ==================================================

const styles = {
  page: {
    padding: "24px",
    backgroundColor: "#f5f6f8",
    minHeight: "100vh",
    fontFamily: "Arial, sans-serif"
  },

  center: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center"
  },

  loading: {
    fontSize: "18px"
  },

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "20px"
  },

  title: {
    margin: 0,
    fontSize: "30px"
  },

  subtitle: {
    marginTop: "6px",
    color: "#666"
  },

  headerButtons: {
    display: "flex",
    gap: "10px"
  },

  primaryButton: {
    backgroundColor: "#000",
    color: "#fff",
    border: "none",
    padding: "11px 18px",
    borderRadius: "7px",
    cursor: "pointer",
    fontWeight: "bold"
  },

  secondaryButton: {
    backgroundColor: "#fff",
    border: "1px solid #ccc",
    padding: "11px 18px",
    borderRadius: "7px",
    cursor: "pointer"
  },

  error: {
    backgroundColor: "#ffe5e5",
    color: "#a00000",
    padding: "12px",
    borderRadius: "7px",
    marginBottom: "15px"
  },

  statsGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(4, 1fr)",
    gap: "12px",
    marginBottom: "20px"
  },

  statCard: {
    backgroundColor: "#fff",
    border: "1px solid #ddd",
    borderRadius: "10px",
    padding: "18px"
  },

  statTitle: {
    color: "#666",
    fontSize: "13px"
  },

  statValue: {
    fontSize: "25px",
    fontWeight: "bold",
    marginTop: "8px"
  },

  filterCard: {
    backgroundColor: "#fff",
    border: "1px solid #ddd",
    borderRadius: "10px",
    padding: "15px",
    display: "flex",
    gap: "12px",
    marginBottom: "15px"
  },

  searchInput: {
    flex: 1,
    padding: "12px",
    border: "1px solid #ccc",
    borderRadius: "7px",
    fontSize: "14px"
  },

  select: {
    padding: "12px",
    border: "1px solid #ccc",
    borderRadius: "7px",
    backgroundColor: "#fff"
  },

  tableCard: {
    backgroundColor: "#fff",
    border: "1px solid #ddd",
    borderRadius: "10px",
    overflow: "auto"
  },

  table: {
    width: "100%",
    borderCollapse: "collapse",
    minWidth: "1300px"
  },

  th: {
    textAlign: "left",
    padding: "14px",
    borderBottom: "1px solid #ddd",
    backgroundColor: "#f8f8f8",
    fontSize: "13px",
    whiteSpace: "nowrap"
  },

  td: {
    padding: "14px",
    borderBottom: "1px solid #eee",
    fontSize: "13px",
    verticalAlign: "top"
  },

  rideId: {
    fontWeight: "bold"
  },

  rideDate: {
    color: "#777",
    fontSize: "11px",
    marginTop: "5px"
  },

  name: {
    fontWeight: "bold"
  },

  smallText: {
    color: "#777",
    fontSize: "11px",
    marginTop: "4px"
  },

  routeCell: {
    padding: "14px",
    borderBottom: "1px solid #eee",
    maxWidth: "280px",
    lineHeight: "1.4"
  },

  pickupDot: {
    marginRight: "7px"
  },

  dropDot: {
    marginRight: "7px"
  },

  routeLine: {
    color: "#aaa",
    marginLeft: "3px",
    height: "8px"
  },

  fare: {
    fontWeight: "bold"
  },

  badge: {
    display: "inline-block",
    padding: "5px 9px",
    borderRadius: "20px",
    fontSize: "11px",
    fontWeight: "bold",
    whiteSpace: "nowrap"
  },

  requestedBadge: {
    backgroundColor: "#fff2d6",
    color: "#8a5700"
  },

  acceptedBadge: {
    backgroundColor: "#e5efff",
    color: "#164c9c"
  },

  inProgressBadge: {
    backgroundColor: "#e5f7e8",
    color: "#08751a"
  },

  completedBadge: {
    backgroundColor: "#dff7e4",
    color: "#08751a"
  },

  cancelledBadge: {
    backgroundColor: "#ffe5e5",
    color: "#a00000"
  },

  defaultBadge: {
    backgroundColor: "#eee",
    color: "#555"
  },

  typeBadge: {
    display: "inline-block",
    padding: "5px 9px",
    backgroundColor: "#f0f0f0",
    borderRadius: "15px",
    fontSize: "11px"
  },

  paymentBadge: {
    display: "inline-block",
    padding: "5px 9px",
    borderRadius: "15px",
    fontSize: "11px",
    fontWeight: "bold"
  },

  paidBadge: {
    backgroundColor: "#e5f7e8",
    color: "#08751a"
  },

  failedBadge: {
    backgroundColor: "#ffe5e5",
    color: "#a00000"
  },

  pendingPaymentBadge: {
    backgroundColor: "#fff2d6",
    color: "#8a5700"
  },

  actions: {
    display: "flex",
    gap: "6px",
    flexWrap: "wrap"
  },

  viewButton: {
    padding: "7px 10px",
    border: "1px solid #bbb",
    backgroundColor: "#fff",
    borderRadius: "5px",
    cursor: "pointer"
  },

  cancelButton: {
    padding: "7px 10px",
    border: "none",
    backgroundColor: "#ffe5e5",
    color: "#a00000",
    borderRadius: "5px",
    cursor: "pointer"
  },

  empty: {
    padding: "50px",
    textAlign: "center",
    color: "#666"
  },

  modalOverlay: {
    position: "fixed",
    inset: 0,
    backgroundColor:
      "rgba(0,0,0,0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000
  },

  modal: {
    width: "650px",
    maxWidth: "92%",
    maxHeight: "90vh",
    overflowY: "auto",
    backgroundColor: "#fff",
    borderRadius: "12px",
    boxShadow:
      "0 10px 40px rgba(0,0,0,0.25)"
  },

  modalHeader: {
    padding: "18px 20px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottom: "1px solid #eee"
  },

  modalSubtitle: {
    color: "#777",
    fontSize: "13px",
    marginTop: "4px"
  },

  closeButton: {
    border: "none",
    background: "transparent",
    fontSize: "28px",
    cursor: "pointer"
  },

  modalBody: {
    padding: "20px"
  },

  sectionTitle: {
    fontSize: "15px",
    marginTop: "22px",
    marginBottom: "5px",
    borderBottom: "1px solid #ddd",
    paddingBottom: "7px"
  },

  detailRow: {
    display: "flex",
    justifyContent: "space-between",
    gap: "20px",
    padding: "10px 0",
    borderBottom: "1px solid #eee"
  },

  detailLabel: {
    color: "#666",
    fontWeight: "bold",
    minWidth: "150px"
  },

  detailValue: {
    textAlign: "right",
    wordBreak: "break-word"
  },

  modalFooter: {
    padding: "15px 20px",
    borderTop: "1px solid #eee",
    display: "flex",
    justifyContent: "flex-end",
    gap: "10px"
  },

  cancelButtonLarge: {
    padding: "10px 15px",
    border: "none",
    backgroundColor: "#ffe5e5",
    color: "#a00000",
    borderRadius: "6px",
    cursor: "pointer"
  },

  closeModalButton: {
    padding: "10px 15px",
    border: "1px solid #bbb",
    backgroundColor: "#fff",
    borderRadius: "6px",
    cursor: "pointer"
  }
};
