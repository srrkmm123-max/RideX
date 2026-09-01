import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000/api/v1";

export default function Users() {

  const [users, setUsers] = useState([]);

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [search, setSearch] =
    useState("");

  const [statusFilter, setStatusFilter] =
    useState("all");

  const [selectedUser, setSelectedUser] =
    useState(null);

  const [error, setError] =
    useState("");


  // ==================================================
  // GET ADMIN TOKEN
  // ==================================================

  const getToken = () => {

    return localStorage.getItem(
      "admin_token"
    );

  };


  // ==================================================
  // API CONFIG
  // ==================================================

  const getConfig = () => {

    const token =
      getToken();

    return {

      headers: {

        Authorization:
          `Bearer ${token}`,

        "Content-Type":
          "application/json"

      }

    };

  };


  // ==================================================
  // LOAD USERS
  // ==================================================

  const loadUsers = useCallback(
    async () => {

      try {

        setError("");

        const response =
          await axios.get(

            `${API_URL}/admin/users`,

            getConfig()

          );


        setUsers(
          response.data.users || []
        );

      } catch (err) {

        console.error(
          "Load users error:",
          err
        );


        setError(
          err.response?.data?.detail ||
          "Unable to load users."
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

  useEffect(() => {

    loadUsers();

  }, [loadUsers]);


  // ==================================================
  // REFRESH
  // ==================================================

  const refreshUsers = () => {

    setRefreshing(true);

    loadUsers();

  };


  // ==================================================
  // FILTER USERS
  // ==================================================

  const filteredUsers =
    users.filter(user => {

      const searchText =
        search.toLowerCase().trim();


      const matchesSearch =

        !searchText ||

        String(
          user.id || ""
        )
          .toLowerCase()
          .includes(searchText) ||

        String(
          user.name || ""
        )
          .toLowerCase()
          .includes(searchText) ||

        String(
          user.email || ""
        )
          .toLowerCase()
          .includes(searchText) ||

        String(
          user.phone || ""
        )
          .toLowerCase()
          .includes(searchText);


      const matchesStatus =

        statusFilter === "all" ||

        user.status === statusFilter;


      return (
        matchesSearch &&
        matchesStatus
      );

    });


  // ==================================================
  // USER STATUS
  // ==================================================

  const updateUserStatus =
    async (user, newStatus) => {

      try {

        await axios.patch(

          `${API_URL}/admin/users/${user.id}/status`,

          {

            status:
              newStatus

          },

          getConfig()

        );


        setUsers(
          previousUsers =>

            previousUsers.map(
              currentUser =>

                currentUser.id === user.id

                  ? {

                      ...currentUser,

                      status:
                        newStatus

                    }

                  : currentUser

            )

        );


        if (
          selectedUser?.id ===
          user.id
        ) {

          setSelectedUser({

            ...selectedUser,

            status:
              newStatus

          });

        }

      } catch (err) {

        console.error(
          "Update user status error:",
          err
        );


        alert(

          err.response?.data?.detail ||

          "Unable to update user status."

        );

      }

    };


  // ==================================================
  // DELETE USER
  // ==================================================

  const deleteUser =
    async user => {

      const confirmed =
        window.confirm(

          `Delete user "${user.name}"? This action may be irreversible.`

        );


      if (!confirmed) {

        return;

      }


      try {

        await axios.delete(

          `${API_URL}/admin/users/${user.id}`,

          getConfig()

        );


        setUsers(

          previousUsers =>

            previousUsers.filter(
              currentUser =>
                currentUser.id !==
                user.id
            )

        );


        setSelectedUser(null);

      } catch (err) {

        console.error(
          "Delete user error:",
          err
        );


        alert(

          err.response?.data?.detail ||

          "Unable to delete user."

        );

      }

    };


  // ==================================================
  // VIEW USER
  // ==================================================

  const viewUser =
    async user => {

      try {

        const response =
          await axios.get(

            `${API_URL}/admin/users/${user.id}`,

            getConfig()

          );


        setSelectedUser(
          response.data
        );

      } catch (err) {

        console.error(
          "View user error:",
          err
        );


        setSelectedUser(
          user
        );

      }

    };


  // ==================================================
  // EXPORT CSV
  // ==================================================

  const exportUsers =
    () => {

      if (
        filteredUsers.length === 0
      ) {

        alert(
          "No users to export."
        );

        return;

      }


      const headers = [

        "ID",
        "Name",
        "Email",
        "Phone",
        "Status",
        "Created At"

      ];


      const rows =
        filteredUsers.map(
          user => [

            user.id || "",

            user.name || "",

            user.email || "",

            user.phone || "",

            user.status || "",

            user.created_at || ""

          ]

        );


      const csv = [

        headers,

        ...rows

      ]

        .map(row =>

          row.map(value =>

            `"${String(value)
              .replace(/"/g, '""')}"`

          ).join(",")

        )

        .join("\n");


      const blob =
        new Blob(
          [csv],
          {
            type:
              "text/csv;charset=utf-8;"
          }
        );


      const url =
        URL.createObjectURL(blob);


      const link =
        document.createElement("a");


      link.href =
        url;

      link.download =
        "ridex-users.csv";

      link.click();


      URL.revokeObjectURL(url);

    };


  // ==================================================
  // STATISTICS
  // ==================================================

  const totalUsers =
    users.length;


  const activeUsers =
    users.filter(
      user =>
        user.status === "active"
    ).length;


  const blockedUsers =
    users.filter(
      user =>
        user.status === "blocked"
    ).length;


  const suspendedUsers =
    users.filter(
      user =>
        user.status === "suspended"
    ).length;


  // ==================================================
  // LOADING
  // ==================================================

  if (loading) {

    return (

      <div style={styles.center}>

        <div style={styles.spinner}>
          Loading users...
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
            Users
          </h1>

          <p style={styles.subtitle}>
            Manage RideX passenger accounts
          </p>

        </div>


        <div style={styles.headerButtons}>

          <button
            style={styles.secondaryButton}
            onClick={refreshUsers}
            disabled={refreshing}
          >

            {refreshing
              ? "Refreshing..."
              : "↻ Refresh"}

          </button>


          <button
            style={styles.primaryButton}
            onClick={exportUsers}
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
          title="Total Users"
          value={totalUsers}
        />


        <StatCard
          title="Active"
          value={activeUsers}
        />


        <StatCard
          title="Blocked"
          value={blockedUsers}
        />


        <StatCard
          title="Suspended"
          value={suspendedUsers}
        />


      </div>


      {/* FILTERS */}

      <div style={styles.filterCard}>


        <input

          type="text"

          placeholder="Search by name, email, phone or ID..."

          value={search}

          onChange={event =>
            setSearch(
              event.target.value
            )
          }

          style={styles.searchInput}

        />


        <select

          value={statusFilter}

          onChange={event =>
            setStatusFilter(
              event.target.value
            )
          }

          style={styles.select}

        >

          <option value="all">
            All Status
          </option>

          <option value="active">
            Active
          </option>

          <option value="blocked">
            Blocked
          </option>

          <option value="suspended">
            Suspended
          </option>

        </select>


      </div>


      {/* USER TABLE */}

      <div style={styles.tableCard}>

        <table style={styles.table}>

          <thead>

            <tr>

              <th style={styles.th}>
                ID
              </th>

              <th style={styles.th}>
                User
              </th>

              <th style={styles.th}>
                Contact
              </th>

              <th style={styles.th}>
                Status
              </th>

              <th style={styles.th}>
                Rides
              </th>

              <th style={styles.th}>
                Joined
              </th>

              <th style={styles.th}>
                Actions
              </th>

            </tr>

          </thead>


          <tbody>

            {filteredUsers.map(user => (

              <tr key={user.id}>

                <td style={styles.td}>

                  #{user.id}

                </td>


                <td style={styles.td}>

                  <div style={styles.userName}>

                    {user.name ||
                      "Unknown"}

                  </div>

                  <div style={styles.userEmail}>

                    {user.email ||
                      "No email"}

                  </div>

                </td>


                <td style={styles.td}>

                  {user.phone ||
                    "No phone"}

                </td>


                <td style={styles.td}>

                  <StatusBadge
                    status={
                      user.status
                    }
                  />

                </td>


                <td style={styles.td}>

                  {user.total_rides ??
                    0}

                </td>


                <td style={styles.td}>

                  {user.created_at ||
                    "-"}

                </td>


                <td style={styles.td}>

                  <div style={styles.actions}>


                    <button

                      style={
                        styles.viewButton
                      }

                      onClick={() =>
                        viewUser(user)
                      }

                    >

                      View

                    </button>


                    {user.status ===
                      "active" ? (

                      <button

                        style={
                          styles.warningButton
                        }

                        onClick={() =>
                          updateUserStatus(
                            user,
                            "blocked"
                          )
                        }

                      >

                        Block

                      </button>

                    ) : (

                      <button

                        style={
                          styles.successButton
                        }

                        onClick={() =>
                          updateUserStatus(
                            user,
                            "active"
                          )
                        }

                      >

                        Activate

                      </button>

                    )}


                    <button

                      style={
                        styles.deleteButton
                      }

                      onClick={() =>
                        deleteUser(user)
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


        {filteredUsers.length === 0 && (

          <div style={styles.empty}>

            <h3>
              No users found
            </h3>

            <p>
              Try changing your search
              or status filter.
            </p>

          </div>

        )}

      </div>


      {/* USER DETAILS MODAL */}

      {selectedUser && (

        <div style={styles.modalOverlay}>

          <div style={styles.modal}>


            <div style={styles.modalHeader}>

              <h2>
                User Details
              </h2>


              <button

                style={styles.closeButton}

                onClick={() =>
                  setSelectedUser(null)
                }

              >

                ×

              </button>

            </div>


            <div style={styles.modalBody}>


              <DetailRow
                label="User ID"
                value={
                  `#${selectedUser.id}`
                }
              />


              <DetailRow
                label="Name"
                value={
                  selectedUser.name
                }
              />


              <DetailRow
                label="Email"
                value={
                  selectedUser.email
                }
              />


              <DetailRow
                label="Phone"
                value={
                  selectedUser.phone
                }
              />


              <DetailRow
                label="Status"
                value={
                  selectedUser.status
                }
              />


              <DetailRow
                label="Total Rides"
                value={
                  selectedUser.total_rides ??
                  0
                }
              />


              <DetailRow
                label="Cancelled Rides"
                value={
                  selectedUser.cancelled_rides ??
                  0
                }
              />


              <DetailRow
                label="Created"
                value={
                  selectedUser.created_at
                }
              />


              <DetailRow
                label="Last Login"
                value={
                  selectedUser.last_login ||
                  "-"
                }
              />


            </div>


            <div style={styles.modalFooter}>


              {selectedUser.status ===
                "active" ? (

                <button

                  style={
                    styles.warningButtonLarge
                  }

                  onClick={() =>

                    updateUserStatus(
                      selectedUser,
                      "blocked"
                    )

                  }

                >

                  Block User

                </button>

              ) : (

                <button

                  style={
                    styles.successButtonLarge
                  }

                  onClick={() =>

                    updateUserStatus(
                      selectedUser,
                      "active"
                    )

                  }

                >

                  Activate User

                </button>

              )}


              <button

                style={styles.closeModalButton}

                onClick={() =>
                  setSelectedUser(null)
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

  const normalizedStatus =
    status || "unknown";


  return (

    <span

      style={{
        ...styles.statusBadge,

        ...(normalizedStatus === "active"
          ? styles.activeBadge
          : normalizedStatus === "blocked"
            ? styles.blockedBadge
            : normalizedStatus === "suspended"
              ? styles.suspendedBadge
              : styles.unknownBadge)
      }}

    >

      {normalizedStatus}

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

    fontFamily:
      "Arial, sans-serif"

  },

  center: {

    minHeight: "100vh",

    display: "flex",

    alignItems: "center",

    justifyContent: "center"

  },

  spinner: {

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

    gap: "15px",

    marginBottom: "20px"

  },

  statCard: {

    backgroundColor: "#fff",

    border: "1px solid #ddd",

    borderRadius: "10px",

    padding: "20px"

  },

  statTitle: {

    color: "#666",

    fontSize: "14px"

  },

  statValue: {

    fontSize: "28px",

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

    fontSize: "13px"

  },

  td: {

    padding: "14px",

    borderBottom: "1px solid #eee",

    fontSize: "14px"

  },

  userName: {

    fontWeight: "bold"

  },

  userEmail: {

    color: "#777",

    fontSize: "12px",

    marginTop: "4px"

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

  blockedBadge: {

    backgroundColor: "#ffe5e5",

    color: "#a00000"

  },

  suspendedBadge: {

    backgroundColor: "#fff2d6",

    color: "#8a5700"

  },

  unknownBadge: {

    backgroundColor: "#eee",

    color: "#555"

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

    backgroundColor:
      "rgba(0,0,0,0.5)",

    display: "flex",

    alignItems: "center",

    justifyContent: "center",

    zIndex: 1000

  },

  modal: {

    width: "520px",

    maxWidth: "90%",

    backgroundColor: "#fff",

    borderRadius: "12px",

    overflow: "hidden",

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
