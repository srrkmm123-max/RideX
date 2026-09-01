import React, { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000/api/v1";

export default function Reports() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const [period, setPeriod] = useState("30d");

  // ==================================================
  // AUTH
  // ==================================================

  const getToken = () => {
    return localStorage.getItem("admin_token");
  };

  const getConfig = () => ({
    headers: {
      Authorization: `Bearer ${getToken()}`,
      "Content-Type": "application/json"
    }
  });

  // ==================================================
  // LOAD REPORT
  // ==================================================

  const loadReport = useCallback(async () => {
    try {
      setError("");

      const response = await axios.get(
        `${API_URL}/admin/reports?period=${period}`,
        getConfig()
      );

      setReport(response.data);
    } catch (err) {
      console.error("Load report error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to load reports."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [period]);

  useEffect(() => {
    loadReport();
  }, [loadReport]);

  // ==================================================
  // REFRESH
  // ==================================================

  const refreshReport = () => {
    setRefreshing(true);
    loadReport();
  };

  // ==================================================
  // EXPORT REPORT
  // ==================================================

  const exportReport = () => {
    if (!report) {
      alert("No report data available.");
      return;
    }

    const rows = [
      ["RideX Report"],
      ["Period", report.period || period],
      [],
      ["KPI", "Value"],
      ["Total Rides", report.summary?.total_rides || 0],
      ["Completed Rides", report.summary?.completed_rides || 0],
      ["Cancelled Rides", report.summary?.cancelled_rides || 0],
      ["Active Drivers", report.summary?.active_drivers || 0],
      ["Total Passengers", report.summary?.total_passengers || 0],
      ["Gross Revenue", report.summary?.gross_revenue || 0],
      ["Refunds", report.summary?.refunds || 0],
      ["Net Revenue", report.summary?.net_revenue || 0],
      ["Average Fare", report.summary?.average_fare || 0],
      ["Cancellation Rate", report.summary?.cancellation_rate || 0],
      []
    ];

    if (report.daily_trends?.length) {
      rows.push([
        "Date",
        "Rides",
        "Completed",
        "Cancelled",
        "Revenue"
      ]);

      report.daily_trends.forEach((item) => {
        rows.push([
          item.date || "",
          item.rides || 0,
          item.completed || 0,
          item.cancelled || 0,
          item.revenue || 0
        ]);
      });
    }

    const csv = rows
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
    link.download = `ridex-report-${period}.csv`;

    link.click();

    URL.revokeObjectURL(url);
  };

  // ==================================================
  // FALLBACK DATA
  // ==================================================

  const summary = report?.summary || {};

  const dailyTrends = report?.daily_trends || [];

  const driverPerformance =
    report?.driver_performance || [];

  const paymentMethods =
    report?.payment_methods || [];

  const rideTypes =
    report?.ride_types || [];

  const topDrivers =
    useMemo(() => {
      return [...driverPerformance]
        .sort(
          (a, b) =>
            Number(b.revenue || 0) -
            Number(a.revenue || 0)
        )
        .slice(0, 10);
    }, [driverPerformance]);

  const maxDailyRevenue = Math.max(
    ...dailyTrends.map((item) =>
      Number(item.revenue || 0)
    ),
    1
  );

  // ==================================================
  // LOADING
  // ==================================================

  if (loading) {
    return (
      <div style={styles.center}>
        <div style={styles.loading}>
          Loading reports...
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
            Reports & Analytics
          </h1>

          <p style={styles.subtitle}>
            RideX business, ride and driver
            performance
          </p>
        </div>

        <div style={styles.headerButtons}>

          <select
            value={period}
            onChange={(event) =>
              setPeriod(event.target.value)
            }
            style={styles.periodSelect}
          >
            <option value="7d">
              Last 7 Days
            </option>

            <option value="30d">
              Last 30 Days
            </option>

            <option value="90d">
              Last 90 Days
            </option>

            <option value="1y">
              Last 1 Year
            </option>
          </select>

          <button
            style={styles.secondaryButton}
            onClick={refreshReport}
            disabled={refreshing}
          >
            {refreshing
              ? "Refreshing..."
              : "↻ Refresh"}
          </button>

          <button
            style={styles.primaryButton}
            onClick={exportReport}
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

      {/* ==================================================
          KPI CARDS
          ================================================== */}

      <div style={styles.kpiGrid}>

        <KpiCard
          title="Total Rides"
          value={formatNumber(
            summary.total_rides
          )}
          subtitle={`${formatNumber(
            summary.completed_rides
          )} completed`}
        />

        <KpiCard
          title="Gross Revenue"
          value={formatCurrency(
            summary.gross_revenue
          )}
          subtitle={`${formatCurrency(
            summary.average_fare
          )} average fare`}
        />

        <KpiCard
          title="Net Revenue"
          value={formatCurrency(
            summary.net_revenue
          )}
          subtitle={`${formatCurrency(
            summary.refunds
          )} refunds`}
        />

        <KpiCard
          title="Cancellation Rate"
          value={`${Number(
            summary.cancellation_rate || 0
          ).toFixed(1)}%`}
          subtitle={`${formatNumber(
            summary.cancelled_rides
          )} cancelled`}
        />

        <KpiCard
          title="Active Drivers"
          value={formatNumber(
            summary.active_drivers
          )}
          subtitle={`${formatNumber(
            summary.online_drivers
          )} online`}
        />

        <KpiCard
          title="Passengers"
          value={formatNumber(
            summary.total_passengers
          )}
          subtitle={`${formatNumber(
            summary.new_passengers
          )} new`}
        />

      </div>

      {/* ==================================================
          DAILY REVENUE
          ================================================== */}

      <div style={styles.card}>

        <div style={styles.cardHeader}>

          <div>
            <h2 style={styles.cardTitle}>
              Daily Revenue
            </h2>

            <p style={styles.cardSubtitle}>
              Revenue performance over the
              selected period
            </p>
          </div>

          <strong>
            {formatCurrency(
              summary.net_revenue
            )}
          </strong>

        </div>

        <div style={styles.chart}>

          {dailyTrends.length === 0 ? (

            <EmptyChart />

          ) : (

            dailyTrends.map(
              (item, index) => {

                const revenue =
                  Number(
                    item.revenue || 0
                  );

                const height =
                  Math.max(
                    (revenue /
                      maxDailyRevenue) *
                      100,
                    4
                  );

                return (
                  <div
                    key={
                      item.date ||
                      index
                    }
                    style={styles.chartColumn}
                  >

                    <div
                      style={{
                        ...styles.bar,
                        height: `${height}%`
                      }}
                      title={`${formatCurrency(
                        revenue
                      )}`}
                    />

                    <div
                      style={
                        styles.chartLabel
                      }
                    >
                      {formatShortDate(
                        item.date
                      )}
                    </div>

                  </div>
                );
              }
            )

          )}

        </div>

      </div>

      {/* ==================================================
          RIDE TREND
          ================================================== */}

      <div style={styles.card}>

        <div style={styles.cardHeader}>

          <div>
            <h2 style={styles.cardTitle}>
              Ride Trend
            </h2>

            <p style={styles.cardSubtitle}>
              Daily completed and cancelled
              rides
            </p>
          </div>

        </div>

        <div style={styles.trendTable}>

          <div style={styles.trendHeader}>
            <span>Date</span>
            <span>Total</span>
            <span>Completed</span>
            <span>Cancelled</span>
            <span>Revenue</span>
          </div>

          {dailyTrends
            .slice()
            .reverse()
            .slice(0, 15)
            .map((item, index) => (

              <div
                key={
                  item.date ||
                  index
                }
                style={styles.trendRow}
              >

                <span>
                  {formatDate(
                    item.date
                  )}
                </span>

                <span>
                  {formatNumber(
                    item.rides
                  )}
                </span>

                <span style={styles.completedText}>
                  {formatNumber(
                    item.completed
                  )}
                </span>

                <span style={styles.cancelledText}>
                  {formatNumber(
                    item.cancelled
                  )}
                </span>

                <span>
                  {formatCurrency(
                    item.revenue
                  )}
                </span>

              </div>

            ))}

        </div>

      </div>

      {/* ==================================================
          TWO COLUMN SECTION
          ================================================== */}

      <div style={styles.twoColumns}>

        {/* PAYMENT METHODS */}

        <div style={styles.card}>

          <div style={styles.cardHeader}>
            <div>
              <h2 style={styles.cardTitle}>
                Payment Methods
              </h2>

              <p style={styles.cardSubtitle}>
                Revenue by payment method
              </p>
            </div>
          </div>

          {paymentMethods.length === 0 ? (

            <EmptyChart />

          ) : (

            <div>

              {paymentMethods.map(
                (item, index) => {

                  const percentage =
                    Number(
                      item.percentage ||
                        calculatePercentage(
                          item.amount,
                          summary.gross_revenue
                        )
                    );

                  return (
                    <div
                      key={
                        item.method ||
                        index
                      }
                      style={
                        styles.progressItem
                      }
                    >

                      <div
                        style={
                          styles.progressHeader
                        }
                      >

                        <span>
                          {formatStatus(
                            item.method
                          )}
                        </span>

                        <strong>
                          {formatCurrency(
                            item.amount
                          )}
                        </strong>

                      </div>

                      <div
                        style={
                          styles.progressBackground
                        }
                      >

                        <div
                          style={{
                            ...styles.progressBar,
                            width: `${Math.min(
                              percentage,
                              100
                            )}%`
                          }}
                        />

                      </div>

                      <div
                        style={
                          styles.progressPercent
                        }
                      >
                        {percentage.toFixed(1)}%
                      </div>

                    </div>
                  );
                }
              )}

            </div>

          )}

        </div>

        {/* RIDE TYPES */}

        <div style={styles.card}>

          <div style={styles.cardHeader}>
            <div>
              <h2 style={styles.cardTitle}>
                Ride Types
              </h2>

              <p style={styles.cardSubtitle}>
                Distribution by ride category
              </p>
            </div>
          </div>

          {rideTypes.length === 0 ? (

            <EmptyChart />

          ) : (

            <div>

              {rideTypes.map(
                (item, index) => {

                  const percentage =
                    Number(
                      item.percentage ||
                        calculatePercentage(
                          item.rides,
                          summary.total_rides
                        )
                    );

                  return (
                    <div
                      key={
                        item.type ||
                        index
                      }
                      style={
                        styles.progressItem
                      }
                    >

                      <div
                        style={
                          styles.progressHeader
                        }
                      >

                        <span>
                          {formatStatus(
                            item.type
                          )}
                        </span>

                        <strong>
                          {formatNumber(
                            item.rides
                          )} rides
                        </strong>

                      </div>

                      <div
                        style={
                          styles.progressBackground
                        }
                      >

                        <div
                          style={{
                            ...styles.progressBar,
                            width: `${Math.min(
                              percentage,
                              100
                            )}%`
                          }}
                        />

                      </div>

                      <div
                        style={
                          styles.progressPercent
                        }
                      >
                        {percentage.toFixed(1)}%
                      </div>

                    </div>
                  );
                }
              )}

            </div>

          )}

        </div>

      </div>

      {/* ==================================================
          DRIVER PERFORMANCE
          ================================================== */}

      <div style={styles.card}>

        <div style={styles.cardHeader}>

          <div>
            <h2 style={styles.cardTitle}>
              Top Driver Performance
            </h2>

            <p style={styles.cardSubtitle}>
              Drivers ranked by revenue
            </p>
          </div>

        </div>

        <div style={styles.tableWrapper}>

          <table style={styles.table}>

            <thead>

              <tr>

                <th style={styles.th}>
                  Rank
                </th>

                <th style={styles.th}>
                  Driver
                </th>

                <th style={styles.th}>
                  Rides
                </th>

                <th style={styles.th}>
                  Completed
                </th>

                <th style={styles.th}>
                  Cancelled
                </th>

                <th style={styles.th}>
                  Rating
                </th>

                <th style={styles.th}>
                  Revenue
                </th>

                <th style={styles.th}>
                  Completion
                </th>

              </tr>

            </thead>

            <tbody>

              {topDrivers.map(
                (driver, index) => {

                  const completion =
                    Number(
                      driver.completion_rate ||
                        calculatePercentage(
                          driver.completed_rides,
                          driver.rides
                        )
                    );

                  return (
                    <tr
                      key={
                        driver.driver_id ||
                        index
                      }
                    >

                      <td style={styles.td}>
                        <strong>
                          #{index + 1}
                        </strong>
                      </td>

                      <td style={styles.td}>

                        <div style={styles.driverName}>
                          {driver.driver_name ||
                            "Unknown"}
                        </div>

                        <div
                          style={
                            styles.smallText
                          }
                        >
                          ID:{" "}
                          {driver.driver_id ||
                            "-"}
                        </div>

                      </td>

                      <td style={styles.td}>
                        {formatNumber(
                          driver.rides
                        )}
                      </td>

                      <td
                        style={{
                          ...styles.td,
                          ...styles.completedText
                        }}
                      >
                        {formatNumber(
                          driver.completed_rides
                        )}
                      </td>

                      <td
                        style={{
                          ...styles.td,
                          ...styles.cancelledText
                        }}
                      >
                        {formatNumber(
                          driver.cancelled_rides
                        )}
                      </td>

                      <td style={styles.td}>
                        ★{" "}
                        {Number(
                          driver.rating || 0
                        ).toFixed(1)}
                      </td>

                      <td style={styles.td}>
                        <strong>
                          {formatCurrency(
                            driver.revenue
                          )}
                        </strong>
                      </td>

                      <td style={styles.td}>
                        {completion.toFixed(1)}%
                      </td>

                    </tr>
                  );
                }
              )}

            </tbody>

          </table>

          {topDrivers.length === 0 && (
            <EmptyTable />
          )}

        </div>

      </div>

      {/* ==================================================
          OPERATIONAL KPIs
          ================================================== */}

      <div style={styles.card}>

        <div style={styles.cardHeader}>

          <div>
            <h2 style={styles.cardTitle}>
              Operational KPIs
            </h2>

            <p style={styles.cardSubtitle}>
              Key RideX service-performance
              metrics
            </p>
          </div>

        </div>

        <div style={styles.kpiSmallGrid}>

          <Metric
            title="Average Ride Distance"
            value={`${Number(
              summary.average_distance_km ||
                0
            ).toFixed(1)} km`}
          />

          <Metric
            title="Average Ride Duration"
            value={`${Number(
              summary.average_duration_minutes ||
                0
            ).toFixed(0)} min`}
          />

          <Metric
            title="Average Driver Rating"
            value={`★ ${Number(
              summary.average_driver_rating ||
                0
            ).toFixed(1)}`}
          />

          <Metric
            title="Average Driver ETA"
            value={`${Number(
              summary.average_driver_eta_minutes ||
                0
            ).toFixed(0)} min`}
          />

          <Metric
            title="Driver Acceptance Rate"
            value={`${Number(
              summary.driver_acceptance_rate ||
                0
            ).toFixed(1)}%`}
          />

          <Metric
            title="Ride Completion Rate"
            value={`${Number(
              summary.completion_rate ||
                0
            ).toFixed(1)}%`}
          />

        </div>

      </div>

    </div>
  );
}


// ==================================================
// KPI CARD
// ==================================================

function KpiCard({
  title,
  value,
  subtitle
}) {
  return (
    <div style={styles.kpiCard}>

      <div style={styles.kpiTitle}>
        {title}
      </div>

      <div style={styles.kpiValue}>
        {value}
      </div>

      <div style={styles.kpiSubtitle}>
        {subtitle}
      </div>

    </div>
  );
}


// ==================================================
// METRIC
// ==================================================

function Metric({
  title,
  value
}) {
  return (
    <div style={styles.metricCard}>

      <div style={styles.metricTitle}>
        {title}
      </div>

      <div style={styles.metricValue}>
        {value}
      </div>

    </div>
  );
}


// ==================================================
// EMPTY CHART
// ==================================================

function EmptyChart() {
  return (
    <div style={styles.emptyChart}>
      No data available
    </div>
  );
}


// ==================================================
// EMPTY TABLE
// ==================================================

function EmptyTable() {
  return (
    <div style={styles.emptyChart}>
      No driver data available
    </div>
  );
}


// ==================================================
// FORMAT NUMBER
// ==================================================

function formatNumber(value) {
  return Number(
    value || 0
  ).toLocaleString("en-IN");
}


// ==================================================
// FORMAT CURRENCY
// ==================================================

function formatCurrency(value) {
  return `₹${Number(
    value || 0
  ).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`;
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

  return date.toLocaleDateString(
    "en-IN"
  );
}


// ==================================================
// SHORT DATE
// ==================================================

function formatShortDate(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value).slice(0, 5);
  }

  return date.toLocaleDateString(
    "en-IN",
    {
      day: "2-digit",
      month: "short"
    }
  );
}


// ==================================================
// PERCENTAGE
// ==================================================

function calculatePercentage(
  value,
  total
) {
  const numerator =
    Number(value || 0);

  const denominator =
    Number(total || 0);

  if (denominator === 0) {
    return 0;
  }

  return (
    (numerator / denominator) *
    100
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
    marginBottom: "20px",
    gap: "20px"
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
    gap: "10px",
    alignItems: "center"
  },

  periodSelect: {
    padding: "11px 14px",
    border: "1px solid #ccc",
    borderRadius: "7px",
    backgroundColor: "#fff"
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

  // ==================================================
  // KPI
  // ==================================================

  kpiGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(3, 1fr)",
    gap: "14px",
    marginBottom: "20px"
  },

  kpiCard: {
    backgroundColor: "#fff",
    border: "1px solid #ddd",
    borderRadius: "10px",
    padding: "20px"
  },

  kpiTitle: {
    color: "#666",
    fontSize: "13px"
  },

  kpiValue: {
    fontSize: "27px",
    fontWeight: "bold",
    marginTop: "8px"
  },

  kpiSubtitle: {
    color: "#777",
    fontSize: "12px",
    marginTop: "7px"
  },

  // ==================================================
  // CARD
  // ==================================================

  card: {
    backgroundColor: "#fff",
    border: "1px solid #ddd",
    borderRadius: "10px",
    padding: "20px",
    marginBottom: "20px"
  },

  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "20px"
  },

  cardTitle: {
    margin: 0,
    fontSize: "18px"
  },

  cardSubtitle: {
    color: "#777",
    fontSize: "12px",
    marginTop: "5px"
  },

  // ==================================================
  // REVENUE CHART
  // ==================================================

  chart: {
    height: "260px",
    display: "flex",
    alignItems: "flex-end",
    gap: "7px",
    borderBottom: "1px solid #ddd",
    padding: "20px 10px 0"
  },

  chartColumn: {
    height: "100%",
    flex: 1,
    display: "flex",
    flexDirection: "column",
    justifyContent: "flex-end",
    alignItems: "center",
    minWidth: "12px"
  },

  bar: {
    width: "70%",
    minHeight: "4px",
    backgroundColor: "#222",
    borderRadius: "4px 4px 0 0",
    cursor: "pointer"
  },

  chartLabel: {
    fontSize: "9px",
    color: "#777",
    marginTop: "8px",
    whiteSpace: "nowrap"
  },

  // ==================================================
  // TREND
  // ==================================================

  trendTable: {
    width: "100%"
  },

  trendHeader: {
    display: "grid",
    gridTemplateColumns:
      "2fr 1fr 1fr 1fr 1.5fr",
    gap: "10px",
    padding: "12px",
    backgroundColor: "#f7f7f7",
    fontWeight: "bold",
    fontSize: "12px"
  },

  trendRow: {
    display: "grid",
    gridTemplateColumns:
      "2fr 1fr 1fr 1fr 1.5fr",
    gap: "10px",
    padding: "12px",
    borderBottom: "1px solid #eee",
    fontSize: "13px"
  },

  completedText: {
    color: "#08751a"
  },

  cancelledText: {
    color: "#a00000"
  },

  // ==================================================
  // TWO COLUMNS
  // ==================================================

  twoColumns: {
    display: "grid",
    gridTemplateColumns:
      "1fr 1fr",
    gap: "20px"
  },

  // ==================================================
  // PROGRESS
  // ==================================================

  progressItem: {
    marginBottom: "18px"
  },

  progressHeader: {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: "7px",
    fontSize: "13px"
  },

  progressBackground: {
    height: "9px",
    backgroundColor: "#eee",
    borderRadius: "10px",
    overflow: "hidden"
  },

  progressBar: {
    height: "100%",
    backgroundColor: "#222",
    borderRadius: "10px",
    transition: "width 0.3s ease"
  },

  progressPercent: {
    textAlign: "right",
    fontSize: "11px",
    color: "#777",
    marginTop: "4px"
  },

  // ==================================================
  // DRIVER TABLE
  // ==================================================

  tableWrapper: {
    overflowX: "auto"
  },

  table: {
    width: "100%",
    borderCollapse: "collapse",
    minWidth: "850px"
  },

  th: {
    textAlign: "left",
    padding: "13px",
    borderBottom: "1px solid #ddd",
    backgroundColor: "#f8f8f8",
    fontSize: "12px",
    whiteSpace: "nowrap"
  },

  td: {
    padding: "13px",
    borderBottom: "1px solid #eee",
    fontSize: "13px",
    verticalAlign: "top"
  },

  driverName: {
    fontWeight: "bold"
  },

  smallText: {
    color: "#777",
    fontSize: "11px",
    marginTop: "4px"
  },

  // ==================================================
  // OPERATIONAL KPIs
  // ==================================================

  kpiSmallGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(3, 1fr)",
    gap: "12px"
  },

  metricCard: {
    backgroundColor: "#f8f8f8",
    border: "1px solid #eee",
    borderRadius: "8px",
    padding: "16px"
  },

  metricTitle: {
    color: "#666",
    fontSize: "12px"
  },

  metricValue: {
    fontSize: "21px",
    fontWeight: "bold",
    marginTop: "8px"
  },

  emptyChart: {
    height: "150px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "#777"
  }
};
