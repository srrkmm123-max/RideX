import React, { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000/api/v1";

export default function Payments() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [methodFilter, setMethodFilter] = useState("all");

  const [selectedPayment, setSelectedPayment] = useState(null);

  // ==================================================
  // AUTH
  // ==================================================

  const getToken = () => {
    return localStorage.getItem("admin_token");
  };

  const getConfig = () => {
    return {
      headers: {
        Authorization: `Bearer ${getToken()}`,
        "Content-Type": "application/json"
      }
    };
  };

  // ==================================================
  // LOAD PAYMENTS
  // ==================================================

  const loadPayments = useCallback(async () => {
    try {
      setError("");

      const response = await axios.get(
        `${API_URL}/admin/payments`,
        getConfig()
      );

      setPayments(response.data.payments || []);
    } catch (err) {
      console.error("Load payments error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to load payments."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadPayments();
  }, [loadPayments]);

  // ==================================================
  // REFRESH
  // ==================================================

  const refreshPayments = () => {
    setRefreshing(true);
    loadPayments();
  };

  // ==================================================
  // FILTER PAYMENTS
  // ==================================================

  const filteredPayments = useMemo(() => {
    const searchText = search
      .toLowerCase()
      .trim();

    return payments.filter((payment) => {
      const matchesSearch =
        !searchText ||
        String(payment.id || "")
          .toLowerCase()
          .includes(searchText) ||
        String(payment.transaction_id || "")
          .toLowerCase()
          .includes(searchText) ||
        String(payment.ride_id || "")
          .toLowerCase()
          .includes(searchText) ||
        String(payment.passenger_name || "")
          .toLowerCase()
          .includes(searchText) ||
        String(payment.driver_name || "")
          .toLowerCase()
          .includes(searchText) ||
        String(payment.phone || "")
          .toLowerCase()
          .includes(searchText);

      const matchesStatus =
        statusFilter === "all" ||
        payment.status === statusFilter;

      const matchesMethod =
        methodFilter === "all" ||
        payment.payment_method === methodFilter;

      return (
        matchesSearch &&
        matchesStatus &&
        matchesMethod
      );
    });
  }, [
    payments,
    search,
    statusFilter,
    methodFilter
  ]);

  // ==================================================
  // VIEW PAYMENT
  // ==================================================

  const viewPayment = async (payment) => {
    try {
      const response = await axios.get(
        `${API_URL}/admin/payments/${payment.id}`,
        getConfig()
      );

      setSelectedPayment(response.data);
    } catch (err) {
      console.error(
        "View payment error:",
        err
      );

      setSelectedPayment(payment);
    }
  };

  // ==================================================
  // REFUND PAYMENT
  // ==================================================

  const refundPayment = async (payment) => {
    if (payment.status !== "paid") {
      alert(
        "Only successful payments can be refunded."
      );
      return;
    }

    const amount =
      Number(payment.amount || 0);

    const confirmed = window.confirm(
      `Refund ₹${amount.toFixed(2)} for transaction ${payment.transaction_id || payment.id}?`
    );

    if (!confirmed) {
      return;
    }

    try {
      await axios.post(
        `${API_URL}/admin/payments/${payment.id}/refund`,
        {
          reason:
            "Refund initiated by administrator"
        },
        getConfig()
      );

      setPayments((previousPayments) =>
        previousPayments.map(
          (currentPayment) =>
            currentPayment.id === payment.id
              ? {
                  ...currentPayment,
                  status: "refunded"
                }
              : currentPayment
        )
      );

      if (
        selectedPayment?.id === payment.id
      ) {
        setSelectedPayment({
          ...selectedPayment,
          status: "refunded"
        });
      }
    } catch (err) {
      console.error(
        "Refund payment error:",
        err
      );

      alert(
        err.response?.data?.detail ||
          "Unable to refund payment."
      );
    }
  };

  // ==================================================
  // EXPORT CSV
  // ==================================================

  const exportPayments = () => {
    if (filteredPayments.length === 0) {
      alert("No payments to export.");
      return;
    }

    const headers = [
      "Payment ID",
      "Transaction ID",
      "Ride ID",
      "Passenger",
      "Driver",
      "Amount",
      "Currency",
      "Payment Method",
      "Status",
      "Gateway",
      "Gateway Transaction ID",
      "Created At",
      "Completed At"
    ];

    const rows = filteredPayments.map(
      (payment) => [
        payment.id || "",
        payment.transaction_id || "",
        payment.ride_id || "",
        payment.passenger_name || "",
        payment.driver_name || "",
        payment.amount || "",
        payment.currency || "INR",
        payment.payment_method || "",
        payment.status || "",
        payment.gateway || "",
        payment.gateway_transaction_id || "",
        payment.created_at || "",
        payment.completed_at || ""
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
      "ridex-payments.csv";

    link.click();

    URL.revokeObjectURL(url);
  };

  // ==================================================
  // STATISTICS
  // ==================================================

  const totalAmount = payments.reduce(
    (sum, payment) =>
      sum + Number(payment.amount || 0),
    0
  );

  const successfulAmount =
    payments
      .filter(
        (payment) =>
          payment.status === "paid" ||
          payment.status === "completed"
      )
      .reduce(
        (sum, payment) =>
          sum + Number(payment.amount || 0),
        0
      );

  const refundedAmount =
    payments
      .filter(
        (payment) =>
          payment.status === "refunded"
      )
      .reduce(
        (sum, payment) =>
          sum + Number(payment.amount || 0),
        0
      );

  const pendingAmount =
    payments
      .filter(
        (payment) =>
          payment.status === "pending"
      )
      .reduce(
        (sum, payment) =>
          sum + Number(payment.amount || 0),
        0
      );

  const failedAmount =
    payments
      .filter(
        (payment) =>
          payment.status === "failed"
      )
      .reduce(
        (sum, payment) =>
          sum + Number(payment.amount || 0),
        0
      );

  const successfulCount =
    payments.filter(
      (payment) =>
        payment.status === "paid" ||
        payment.status === "completed"
    ).length;

  const pendingCount =
    payments.filter(
      (payment) =>
        payment.status === "pending"
    ).length;

  const failedCount =
    payments.filter(
      (payment) =>
        payment.status === "failed"
    ).length;

  const refundedCount =
    payments.filter(
      (payment) =>
        payment.status === "refunded"
    ).length;

  // ==================================================
  // LOADING
  // ==================================================

  if (loading) {
    return (
      <div style={styles.center}>
        <div style={styles.loading}>
          Loading payments...
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
            Payments
          </h1>

          <p style={styles.subtitle}>
            Monitor RideX transactions,
            revenue and refunds
          </p>
        </div>

        <div style={styles.headerButtons}>

          <button
            style={styles.secondaryButton}
            onClick={refreshPayments}
            disabled={refreshing}
          >
            {refreshing
              ? "Refreshing..."
              : "↻ Refresh"}
          </button>

          <button
            style={styles.primaryButton}
            onClick={exportPayments}
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
          title="Transactions"
          value={payments.length}
        />

        <StatCard
          title="Successful"
          value={successfulCount}
          amount={formatCurrency(
            successfulAmount
          )}
        />

        <StatCard
          title="Pending"
          value={pendingCount}
          amount={formatCurrency(
            pendingAmount
          )}
        />

        <StatCard
          title="Failed"
          value={failedCount}
          amount={formatCurrency(
            failedAmount
          )}
        />

        <StatCard
          title="Refunded"
          value={refundedCount}
          amount={formatCurrency(
            refundedAmount
          )}
        />

        <StatCard
          title="Gross Amount"
          value={formatCurrency(
            totalAmount
          )}
        />

      </div>

      {/* FILTERS */}

      <div style={styles.filterCard}>

        <input
          type="text"
          placeholder="Search transaction, ride, passenger or driver..."
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

          <option value="paid">
            Paid
          </option>

          <option value="completed">
            Completed
          </option>

          <option value="pending">
            Pending
          </option>

          <option value="failed">
            Failed
          </option>

          <option value="refunded">
            Refunded
          </option>

        </select>

        <select
          value={methodFilter}
          onChange={(event) =>
            setMethodFilter(
              event.target.value
            )
          }
          style={styles.select}
        >
          <option value="all">
            All Methods
          </option>

          <option value="upi">
            UPI
          </option>

          <option value="card">
            Card
          </option>

          <option value="cash">
            Cash
          </option>

          <option value="wallet">
            Wallet
          </option>

          <option value="netbanking">
            Net Banking
          </option>

        </select>

      </div>

      {/* PAYMENT TABLE */}

      <div style={styles.tableCard}>

        <table style={styles.table}>

          <thead>

            <tr>

              <th style={styles.th}>
                Transaction
              </th>

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
                Amount
              </th>

              <th style={styles.th}>
                Method
              </th>

              <th style={styles.th}>
                Status
              </th>

              <th style={styles.th}>
                Date
              </th>

              <th style={styles.th}>
                Actions
              </th>

            </tr>

          </thead>

          <tbody>

            {filteredPayments.map(
              (payment) => (

                <tr key={payment.id}>

                  {/* TRANSACTION */}

                  <td style={styles.td}>

                    <div style={styles.transactionId}>
                      {payment.transaction_id ||
                        `PAY-${payment.id}`}
                    </div>

                    <div style={styles.smallText}>
                      ID: #{payment.id}
                    </div>

                  </td>

                  {/* RIDE */}

                  <td style={styles.td}>

                    <div style={styles.rideId}>
                      {payment.ride_id
                        ? `#${payment.ride_id}`
                        : "-"}
                    </div>

                  </td>

                  {/* PASSENGER */}

                  <td style={styles.td}>

                    <div style={styles.name}>
                      {payment.passenger_name ||
                        "-"}
                    </div>

                    <div style={styles.smallText}>
                      {payment.phone || ""}
                    </div>

                  </td>

                  {/* DRIVER */}

                  <td style={styles.td}>

                    <div style={styles.name}>
                      {payment.driver_name ||
                        "-"}
                    </div>

                  </td>

                  {/* AMOUNT */}

                  <td style={styles.td}>

                    <div style={styles.amount}>
                      {formatCurrency(
                        payment.amount
                      )}
                    </div>

                    <div style={styles.currency}>
                      {payment.currency ||
                        "INR"}
                    </div>

                  </td>

                  {/* METHOD */}

                  <td style={styles.td}>

                    <PaymentMethodBadge
                      method={
                        payment.payment_method
                      }
                    />

                  </td>

                  {/* STATUS */}

                  <td style={styles.td}>

                    <PaymentStatusBadge
                      status={
                        payment.status
                      }
                    />

                  </td>

                  {/* DATE */}

                  <td style={styles.td}>

                    {formatDate(
                      payment.created_at
                    )}

                  </td>

                  {/* ACTIONS */}

                  <td style={styles.td}>

                    <div style={styles.actions}>

                      <button
                        style={
                          styles.viewButton
                        }
                        onClick={() =>
                          viewPayment(payment)
                        }
                      >
                        View
                      </button>

                      {payment.status ===
                        "paid" && (

                        <button
                          style={
                            styles.refundButton
                          }
                          onClick={() =>
                            refundPayment(
                              payment
                            )
                          }
                        >
                          Refund
                        </button>

                      )}

                    </div>

                  </td>

                </tr>

              )
            )}

          </tbody>

        </table>

        {filteredPayments.length === 0 && (
          <div style={styles.empty}>

            <h3>
              No payments found
            </h3>

            <p>
              Try changing your search
              or filters.
            </p>

          </div>
        )}

      </div>

      {/* PAYMENT DETAILS */}

      {selectedPayment && (

        <div style={styles.modalOverlay}>

          <div style={styles.modal}>

            <div style={styles.modalHeader}>

              <div>

                <h2 style={{ margin: 0 }}>
                  Payment Details
                </h2>

                <div
                  style={
                    styles.modalSubtitle
                  }
                >
                  Transaction #
                  {selectedPayment.id}
                </div>

              </div>

              <button
                style={styles.closeButton}
                onClick={() =>
                  setSelectedPayment(
                    null
                  )
                }
              >
                ×
              </button>

            </div>

            <div style={styles.modalBody}>

              <SectionTitle
                title="Transaction"
              />

              <DetailRow
                label="Payment ID"
                value={
                  selectedPayment.id
                    ? `#${selectedPayment.id}`
                    : "-"
                }
              />

              <DetailRow
                label="Transaction ID"
                value={
                  selectedPayment.transaction_id
                }
              />

              <DetailRow
                label="Gateway"
                value={
                  selectedPayment.gateway
                }
              />

              <DetailRow
                label="Gateway Transaction ID"
                value={
                  selectedPayment.gateway_transaction_id
                }
              />

              <DetailRow
                label="Status"
                value={
                  selectedPayment.status
                }
              />

              <SectionTitle
                title="Ride"
              />

              <DetailRow
                label="Ride ID"
                value={
                  selectedPayment.ride_id
                    ? `#${selectedPayment.ride_id}`
                    : "-"
                }
              />

              <DetailRow
                label="Passenger"
                value={
                  selectedPayment.passenger_name
                }
              />

              <DetailRow
                label="Driver"
                value={
                  selectedPayment.driver_name
                }
              />

              <SectionTitle
                title="Payment"
              />

              <DetailRow
                label="Amount"
                value={formatCurrency(
                  selectedPayment.amount
                )}
              />

              <DetailRow
                label="Currency"
                value={
                  selectedPayment.currency ||
                  "INR"
                }
              />

              <DetailRow
                label="Payment Method"
                value={
                  selectedPayment.payment_method
                }
              />

              <DetailRow
                label="Payment Status"
                value={
                  selectedPayment.status
                }
              />

              <DetailRow
                label="Fee"
                value={
                  selectedPayment.processing_fee
                    ? formatCurrency(
                        selectedPayment.processing_fee
                      )
                    : "-"
                }
              />

              <DetailRow
                label="Net Amount"
                value={
                  selectedPayment.net_amount
                    ? formatCurrency(
                        selectedPayment.net_amount
                      )
                    : "-"
                }
              />

              <SectionTitle
                title="Dates"
              />

              <DetailRow
                label="Created"
                value={
                  selectedPayment.created_at
                }
              />

              <DetailRow
                label="Completed"
                value={
                  selectedPayment.completed_at
                }
              />

              <DetailRow
                label="Refunded"
                value={
                  selectedPayment.refunded_at
                }
              />

              <SectionTitle
                title="Refund"
              />

              <DetailRow
                label="Refund Amount"
                value={
                  selectedPayment.refund_amount
                    ? formatCurrency(
                        selectedPayment.refund_amount
                      )
                    : "-"
                }
              />

              <DetailRow
                label="Refund Reason"
                value={
                  selectedPayment.refund_reason
                }
              />

            </div>

            <div style={styles.modalFooter}>

              {selectedPayment.status ===
                "paid" && (

                <button
                  style={
                    styles.refundButtonLarge
                  }
                  onClick={() =>
                    refundPayment(
                      selectedPayment
                    )
                  }
                >
                  Refund Payment
                </button>

              )}

              <button
                style={
                  styles.closeModalButton
                }
                onClick={() =>
                  setSelectedPayment(
                    null
                  )
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

function StatCard({
  title,
  value,
  amount
}) {
  return (
    <div style={styles.statCard}>

      <div style={styles.statTitle}>
        {title}
      </div>

      <div style={styles.statValue}>
        {value}
      </div>

      {amount && (
        <div style={styles.statAmount}>
          {amount}
        </div>
      )}

    </div>
  );
}


// ==================================================
// PAYMENT STATUS
// ==================================================

function PaymentStatusBadge({
  status
}) {
  const value =
    status || "unknown";

  return (
    <span
      style={{
        ...styles.badge,

        ...(value === "paid" ||
        value === "completed"
          ? styles.paidBadge
          : value === "pending"
          ? styles.pendingBadge
          : value === "failed"
          ? styles.failedBadge
          : value === "refunded"
          ? styles.refundedBadge
          : styles.defaultBadge)
      }}
    >
      {formatStatus(value)}
    </span>
  );
}


// ==================================================
// PAYMENT METHOD
// ==================================================

function PaymentMethodBadge({
  method
}) {
  return (
    <span style={styles.methodBadge}>
      {formatStatus(
        method || "unknown"
      )}
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

function DetailRow({
  label,
  value
}) {
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
// FORMAT CURRENCY
// ==================================================

function formatCurrency(value) {
  return `₹${Number(
    value || 0
  ).toFixed(2)}`;
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
      "repeat(3, 1fr)",
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

  statAmount: {
    color: "#555",
    marginTop: "5px",
    fontSize: "13px"
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
    minWidth: "1200px"
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

  transactionId: {
    fontWeight: "bold",
    maxWidth: "180px",
    overflow: "hidden",
    textOverflow: "ellipsis"
  },

  rideId: {
    fontWeight: "bold"
  },

  name: {
    fontWeight: "bold"
  },

  smallText: {
    color: "#777",
    fontSize: "11px",
    marginTop: "4px"
  },

  amount: {
    fontWeight: "bold",
    fontSize: "15px"
  },

  currency: {
    color: "#777",
    fontSize: "11px",
    marginTop: "3px"
  },

  badge: {
    display: "inline-block",
    padding: "5px 9px",
    borderRadius: "20px",
    fontSize: "11px",
    fontWeight: "bold",
    whiteSpace: "nowrap"
  },

  paidBadge: {
    backgroundColor: "#e5f7e8",
    color: "#08751a"
  },

  pendingBadge: {
    backgroundColor: "#fff2d6",
    color: "#8a5700"
  },

  failedBadge: {
    backgroundColor: "#ffe5e5",
    color: "#a00000"
  },

  refundedBadge: {
    backgroundColor: "#e8e8ff",
    color: "#38388f"
  },

  defaultBadge: {
    backgroundColor: "#eee",
    color: "#555"
  },

  methodBadge: {
    display: "inline-block",
    padding: "5px 9px",
    borderRadius: "15px",
    backgroundColor: "#f0f0f0",
    fontSize: "11px"
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

  refundButton: {
    padding: "7px 10px",
    border: "none",
    backgroundColor: "#fff0d5",
    color: "#8a5700",
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
    width: "620px",
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
    backgroundColor: "transparent",
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
    minWidth: "170px"
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

  refundButtonLarge: {
    padding: "10px 15px",
    border: "none",
    backgroundColor: "#fff0d5",
    color: "#8a5700",
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
