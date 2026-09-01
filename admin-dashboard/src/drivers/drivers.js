uimport React, { useCallback, useEffect, useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000/api/v1";

export default function Drivers() {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [availabilityFilter, setAvailabilityFilter] = useState("all");

  const [selectedDriver, setSelectedDriver] = useState(null);
  const [error, setError] = useState("");

  // ==================================================
  // GET ADMIN TOKEN
  // ==================================================

  const getToken = () => {
    return localStorage.getItem("admin_token");
  };

  // ==================================================
  // API CONFIG
  // ==================================================

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
  // LOAD DRIVERS
  // ==================================================

  const loadDrivers = useCallback(async () => {
    try {
      setError("");

      const response = await axios.get(
        `${API_URL}/admin/drivers`,
        getConfig()
      );

      setDrivers(response.data.drivers || []);
    } catch (err) {
      console.error("Load drivers error:", err);

      setError(
        err.response?.data?.detail ||
        "Unable to load drivers."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // ==================================================
  // INITIAL LOAD
  // ==================================================

  useEffect(() => {
    loadDrivers();
  }, [loadDrivers]);

  // ==================================================
  // REFRESH
  // ==================================================

  const refreshDrivers = () => {
    setRefreshing(true);
    loadDrivers();
  };

  // ==================================================
  // FILTER DRIVERS
  // ==================================================

  const filteredDrivers = drivers.filter((driver) => {
    const searchText = search.toLowerCase().trim();

    const matchesSearch =
      !searchText ||
      String(driver.id || "")
        .toLowerCase()
        .includes(searchText) ||
      String(driver.name || "")
        .toLowerCase()
        .includes(searchText) ||
      String(driver.email || "")
        .toLowerCase()
        .includes(searchText) ||
      String(driver.phone || "")
        .toLowerCase()
        .includes(searchText) ||
      String(driver.vehicle_number || "")
        .toLowerCase()
        .includes(searchText);

    const matchesStatus =
      statusFilter === "all" ||
      driver.status === statusFilter;

    const matchesAvailability =
      availabilityFilter === "all" ||
      driver.availability === availabilityFilter;

    return (
      matchesSearch &&
      matchesStatus &&
      matchesAvailability
    );
  });

  // ==================================================
  // UPDATE DRIVER STATUS
  // ==================================================

  const updateDriverStatus = async (driver, newStatus) => {
    try {
      await axios.patch(
        `${API_URL}/admin/drivers/${driver.id}/status`,
        {
          status: newStatus
        },
        getConfig()
      );

      setDrivers((previousDrivers) =>
        previousDrivers.map((currentDriver) =>
          currentDriver.id === driver.id
            ? {
                ...currentDriver,
                status: newStatus
              }
            : currentDriver
        )
      );

      if (selectedDriver?.id === driver.id) {
        setSelectedDriver({
          ...selectedDriver,
          status: newStatus
        });
      }
    } catch (err) {
      console.error(
        "Update driver status error:",
        err
      );

      alert(
        err.response?.data?.detail ||
        "Unable to update driver status."
      );
    }
  };

  // ==================================================
  // APPROVE DRIVER
  // ==================================================

  const approveDriver = async (driver) => {
    try {
      await axios.patch(
        `${API_URL}/admin/drivers/${driver.id}/approve`,
        {},
        getConfig()
      );

      setDrivers((previousDrivers) =>
        previousDrivers.map((currentDriver) =>
          currentDriver.id === driver.id
            ? {
                ...currentDriver,
                status: "active",
                approved: true
              }
            : currentDriver
        )
      );

      if (selectedDriver?.id === driver.id) {
        setSelectedDriver({
          ...selectedDriver,
          status: "active",
          approved: true
        });
      }
    } catch (err) {
      console.error(
        "Approve driver error:",
        err
      );

      alert(
        err.response?.data?.detail ||
        "Unable to approve driver."
      );
    }
  };

  // ==================================================
  // DELETE DRIVER
  // ==================================================

  const deleteDriver = async (driver) => {
    const confirmed = window.confirm(
      `Delete driver "${driver.name}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      await axios.delete(
        `${API_URL}/admin/drivers/${driver.id}`,
        getConfig()
      );

      setDrivers((previousDrivers) =>
        previousDrivers.filter(
          (currentDriver) =>
            currentDriver.id !== driver.id
        )
      );

      setSelectedDriver(null);
    } catch (err) {
      console.error(
        "Delete driver error:",
        err
      );

      alert(
        err.response?.data?.detail ||
        "Unable to delete driver."
      );
    }
  };

  // ==================================================
  // VIEW DRIVER
  // ==================================================

  const viewDriver = async (driver) => {
    try {
      const response = await axios.get(
        `${API_URL}/admin/drivers/${driver.id}`,
        getConfig()
      );

      setSelectedDriver(response.data);
    } catch (err) {
      console.error(
        "View driver error:",
        err
      );

      setSelectedDriver(driver);
    }
  };

  // ==================================================
  // EXPORT CSV
  // ==================================================

  const exportDrivers = () => {
    if (filteredDrivers.length === 0) {
      alert("No drivers to export.");
      return;
    }

    const headers = [
      "ID",
      "Name",
      "Email",
      "Phone",
      "Status",
      "Availability",
      "Vehicle",
      "Vehicle Number",
      "Rating",
      "Total Rides",
      "Created At"
    ];

    const rows = filteredDrivers.map((driver) => [
      driver.id || "",
      driver.name || "",
      driver.email || "",
      driver.phone || "",
      driver.status || "",
      driver.availability || "",
      driver.vehicle_model || "",
      driver.vehicle_number || "",
      driver.rating || "",
      driver.total_rides || 0,
      driver.created_at || ""
    ]);

    const csv = [headers, ...rows]
      .map((row) =>
        row
          .map(
            (value) =>
              `"${String(value).replace(/"/g, '""')}"`
          )
          .join(",")
      )
      .join("\n");

    const blob = new Blob([csv], {
      type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = "ridex-drivers.csv";

    link.click();

    URL.revokeObjectURL(url);
  };

  // ==================================================
  // STATISTICS
  // ==================================================

  const totalDrivers = drivers.length;

  const activeDrivers = drivers.filter(
    (driver) =>
      driver.status === "active"
  ).length;

  const pendingDrivers = drivers.filter(
    (driver) =>
      driver.status === "pending"
  ).length;

  const blockedDrivers = drivers.filter(
    (driver) =>
      driver.status === "blocked"
  ).length;

  const onlineDrivers = drivers.filter(
    (driver) =>
      driver.availability === "online"
  ).length;

  const offlineDrivers = drivers.filter(
    (driver) =>
      driver.availability === "offline"
  ).length;

  // ==================================================
  // LOADING
  // ==================================================

  if (loading) {
    return (
      <div style={styles.center}>
        <div style={styles.loading}>
          Loading drivers...
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
            Drivers
          </h1>

          <p style={styles.subtitle}>
            Manage RideX driver accounts,
            vehicles and availability
          </p>
        </div>

        <div style={styles.headerButtons}>

          <button
            style={styles.secondaryButton}
            onClick={refreshDrivers}
            disabled={refreshing}
          >
            {refreshing
              ? "Refreshing..."
              : "↻ Refresh"}
          </button>

          <button
            style={styles.primaryButton}
            onClick={exportDrivers}
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
          title="Total Drivers"
          value={totalDrivers}
        />

        <StatCard
          title="Active"
          value={activeDrivers}
        />

        <StatCard
          title="Pending Approval"
          value={pendingDrivers}
        />

        <StatCard
          title="Blocked"
          value={blockedDrivers}
        />

        <StatCard
          title="Online Now"
          value={onlineDrivers}
        />

        <StatCard
          title="Offline"
          value={offlineDrivers}
        />

      </div>

      {/* FILTERS */}

      <div style={styles.filterCard}>

        <input
          type="text"
          placeholder="Search name, email, phone, ID or vehicle..."
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
          style={styles.searchInput}
        />

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(event.target.value)
          }
          style={styles.select}
        >
          <option value="all">
            All Status
          </option>

          <option value="active">
            Active
          </option>

          <option value="pending">
            Pending
          </option>

          <option value="blocked">
            Blocked
          </option>

          <option value="suspended">
            Suspended
          </option>
        </select>

        <select
          value={availabilityFilter}
          onChange={(event) =>
            setAvailabilityFilter(
              event.target.value
            )
          }
          style={styles.select}
        >
          <option value="all">
            All Availability
          </option>

          <option value="online">
            Online
          </option>

          <option value="offline">
            Offline
          </option>

          <option value="on_trip">
            On Trip
          </option>
        </select>

      </div>

      {/* DRIVER TABLE */}

      <div style={styles.tableCard}>

        <table style={styles.table}>

          <thead>
            <tr>

              <th style={styles.th}>
                ID
              </th>

              <th style={styles.th}>
                Driver
              </th>

              <th style={styles.th}>
                Vehicle
              </th>

              <th style={styles.th}>
                Status
              </th>

              <th style={styles.th}>
                Availability
              </th>

              <th style={styles.th}>
                Rating
              </th>

              <th style={styles.th}>
                Rides
              </th>

              <th style={styles.th}>
                Actions
              </th>

            </tr>
          </thead>

          <tbody>

            {filteredDrivers.map((driver) => (

              <tr key={driver.id}>

                <td style={styles.td}>
                  #{driver.id}
                </td>

                <td style={styles.td}>

                  <div style={styles.driverName}>
                    {driver.name || "Unknown"}
                  </div>

                  <div style={styles.driverEmail}>
                    {driver.email || "No email"}
                  </div>

                  <div style={styles.driverPhone}>
                    {driver.phone || "No phone"}
                  </div>

                </td>

                <td style={styles.td}>

                  <div>
                    {driver.vehicle_model || "-"}
                  </div>

                  <div style={styles.vehicleNumber}>
                    {driver.vehicle_number || "-"}
                  </div>

                </td>

                <td style={styles.td}>

                  <StatusBadge
                    status={driver.status}
                  />

                </td>

                <td style={styles.td}>

                  <AvailabilityBadge
                    availability={
                      driver.availability
                    }
                  />

                </td>

                <td style={styles.td}>

                  <span style={styles.rating}>
                    ★ {driver.rating || "0.0"}
                  </span>

                </td>

                <td style={styles.td}>
                  {driver.total_rides || 0}
                </td>

                <td style={styles.td}>

                  <div style={styles.actions}>

                    <button
                      style={styles.viewButton}
                      onClick={() =>
                        viewDriver(driver)
                      }
                    >
                      View
                    </button>

                    {driver.status ===
                    "pending" ? (

                      <button
                        style={styles.successButton}
                        onClick={() =>
                          approveDriver(driver)
                        }
                      >
                        Approve
                      </button>

                    ) : driver.status ===
                      "active" ? (

                      <button
                        style={styles.warningButton}
                        onClick={() =>
                          updateDriverStatus(
                            driver,
                            "blocked"
                          )
                        }
                      >
                        Block
                      </button>

                    ) : (

                      <button
                        style={styles.successButton}
                        onClick={() =>
                          updateDriverStatus(
                            driver,
                            "active"
                          )
                        }
                      >
                        Activate
                      </button>

                    )}

                    <button
                      style={styles.deleteButton}
                      onClick={() =>
                        deleteDriver(driver)
                      }
                    >
                      Delete
                    </button>

                  </div>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

        {filteredDrivers.length === 0 && (
          <div style={styles.empty}>

            <h3>
              No drivers found
            </h3>

            <p>
              Try changing your search
              or filters.
            </p>

          </div>
        )}

      </div>

      {/* DRIVER DETAILS */}

      {selectedDriver && (

        <div style={styles.modalOverlay}>

          <div style={styles.modal}>

            <div style={styles.modalHeader}>

              <h2>
                Driver Details
              </h2>

              <button
                style={styles.closeButton}
                onClick={() =>
                  setSelectedDriver(null)
                }
              >
                ×
              </button>

            </div>

            <div style={styles.modalBody}>

              <DetailRow
                label="Driver ID"
                value={`#${selectedDriver.id}`}
              />

              <DetailRow
                label="Name"
                value={selectedDriver.name}
              />

              <DetailRow
                label="Email"
                value={selectedDriver.email}
              />

              <DetailRow
                label="Phone"
                value={selectedDriver.phone}
              />

              <DetailRow
                label="Status"
                value={selectedDriver.status}
              />

              <DetailRow
                label="Availability"
                value={
                  selectedDriver.availability
                }
              />

              <DetailRow
                label="Vehicle"
                value={
                  selectedDriver.vehicle_model
                }
              />

              <DetailRow
                label="Vehicle Number"
                value={
                  selectedDriver.vehicle_number
                }
              />

              <DetailRow
                label="License Number"
                value={
                  selectedDriver.license_number
                }
              />

              <DetailRow
                label="Rating"
                value={
                  selectedDriver.rating
                    ? `★ ${selectedDriver.rating}`
                    : "-"
                }
              />

              <DetailRow
                label="Total Rides"
                value={
                  selectedDriver.total_rides ??
                  0
                }
              />

              <DetailRow
                label="Completed Rides"
                value={
                  selectedDriver.completed_rides ??
                  0
                }
              />

              <DetailRow
                label="Cancelled Rides"
                value={
                  selectedDriver.cancelled_rides ??
                  0
                }
              />

              <DetailRow
                label="Created"
                value={
                  selectedDriver.created_at
                }
              />

              <DetailRow
                label="Last Login"
                value={
                  selectedDriver.last_login ||
                  "-"
                }
              />

            </div>

            <div style={styles.modalFooter}>

              {selectedDriver.status ===
              "pending" && (

                <button
                  style={
                    styles.successButtonLarge
                  }
                  onClick={() =>
                    approveDriver(
                      selectedDriver
                    )
                  }
                >
                  Approve Driver
                </button>

              )}

              {selectedDriver.status ===
              "active" && (

                <button
                  style={
                    styles.warningButtonLarge
                  }
                  onClick={() =>
                    updateDriverStatus(
                      selectedDriver,
                      "blocked"
                    )
                  }
                >
                  Block Driver
                </button>

              )}

              {selectedDriver.status ===
              "blocked" && (

                <button
                  style={
                    styles.successButtonLarge
                  }
                  onClick={() =>
                    updateDriverStatus(
                      selectedDriver,
                      "active"
                    )
                  }
                >
                  Activate Driver
                </button>

              )}

              <button
                style={styles.closeModalButton}
                onClick={() =>
                  setSelectedDriver(null)
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
// STATUS BADGE
// ==================================================

function StatusBadge({ status }) {

  const value = status || "unknown";

  return (
    <span
      style={{
        ...styles.statusBadge,

        ...(value === "active"
          ? styles.activeBadge
          : value === "pending"
          ? styles.pendingBadge
          : value === "blocked"
          ? styles.blockedBadge
          : value === "suspended"
          ? styles.suspendedBadge
          : styles.unknownBadge)
      }}
    >
      {value}
    </span>
  );
}


// ==================================================
// AVAILABILITY BADGE
// ==================================================

function AvailabilityBadge({ availability }) {

  const value =
    availability || "offline";

  return (
    <span
      style={{
        ...styles.availabilityBadge,

        ...(value === "online"
          ? styles.onlineBadge
          : value === "on_trip"
          ? styles.onTripBadge
          : styles.offlineBadge)
      }}
    >
      {value === "on_trip"
        ? "On Trip"
        : value}
    </span>
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
      "repeat(6, 1fr)",
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
    fontSize: "26px",
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
    borderCollapse: "collapse"
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
    fontSize: "14px",
    whiteSpace: "nowrap"
  },

  driverName: {
    fontWeight: "bold"
  },

  driverEmail: {
    color: "#777",
    fontSize: "12px",
    marginTop: "4px"
  },

  driverPhone: {
    color: "#777",
    fontSize: "12px",
    marginTop: "3px"
  },

  vehicleNumber: {
    color: "#777",
    fontSize: "12px",
    marginTop: "4px"
  },

  rating: {
    fontWeight: "bold"
  },

  statusBadge: {
    display: "inline-block",
    padding: "5px 9px",
    borderRadius: "20px",
    fontSize: "12px",
    fontWeight: "bold"
  },

  activeBadge: {
    backgroundColor: "#e5f7e8",
    color: "#08751a"
  },

  pendingBadge: {
    backgroundColor: "#fff2d6",
    color: "#8a5700"
  },

  blockedBadge: {
    backgroundColor: "#ffe5e5",
    color: "#a00000"
  },

  suspendedBadge: {
    backgroundColor: "#f0e5ff",
    color: "#6420a0"
  },

  unknownBadge: {
    backgroundColor: "#eee",
    color: "#555"
  },

  availabilityBadge: {
    display: "inline-block",
    padding: "5px 9px",
    borderRadius: "20px",
    fontSize: "12px",
    fontWeight: "bold"
  },

  onlineBadge: {
    backgroundColor: "#e5f7e8",
    color: "#08751a"
  },

  offlineBadge: {
    backgroundColor: "#eee",
    color: "#555"
  },

  onTripBadge: {
    backgroundColor: "#e5efff",
    color: "#164c9c"
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

  warningButton: {
    padding: "7px 10px",
    border: "none",
    backgroundColor: "#fff0d5",
    color: "#8a5700",
    borderRadius: "5px",
    cursor: "pointer"
  },

  successButton: {
    padding: "7px 10px",
    border: "none",
    backgroundColor: "#e5f7e8",
    color: "#08751a",
    borderRadius: "5px",
    cursor: "pointer"
  },

  deleteButton: {
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
    backgroundColor: "rgba(0,0,0,0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000
  },

  modal: {
    width: "560px",
    maxWidth: "90%",
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

  closeButton: {
    border: "none",
    background: "transparent",
    fontSize: "28px",
    cursor: "pointer"
  },

  modalBody: {
    padding: "20px"
  },

  detailRow: {
    display: "flex",
    justifyContent: "space-between",
    gap: "20px",
    padding: "12px 0",
    borderBottom: "1px solid #eee"
  },

  detailLabel: {
    color: "#666",
    fontWeight: "bold"
  },

  detailValue: {
    textAlign: "right"
  },

  modalFooter: {
    padding: "15px 20px",
    borderTop: "1px solid #eee",
    display: "flex",
    justifyContent: "flex-end",
    gap: "10px"
  },

  warningButtonLarge: {
    padding: "10px 15px",
    border: "none",
    backgroundColor: "#fff0d5",
    color: "#8a5700",
    borderRadius: "6px",
    cursor: "pointer"
  },

  successButtonLarge: {
    padding: "10px 15px",
    border: "none",
    backgroundColor: "#e5f7e8",
    color: "#08751a",
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
