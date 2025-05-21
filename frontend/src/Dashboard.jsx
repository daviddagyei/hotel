import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

const ROOM_URL = 'http://localhost:8001/api/v1/room-service/rooms';
const RESERVATION_URL = 'http://localhost:8002/api/v1/reservations';
const TASK_URL = 'http://localhost:8003/api/v1/tasks';
const REPORT_URL = 'http://localhost:8006/api/v1/reports/occupancy';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [rooms, setRooms] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError('');
      try {
        const [roomsRes, reservationsRes, tasksRes, reportRes] = await Promise.all([
          axios.get(ROOM_URL),
          axios.get(RESERVATION_URL),
          axios.get(TASK_URL),
          axios.get(REPORT_URL).catch(() => ({ data: null })),
        ]);
        setRooms(roomsRes.data);
        setReservations(reservationsRes.data);
        setTasks(tasksRes.data);
        setReport(reportRes.data);
        setStats({
          totalRooms: roomsRes.data.length,
          occupiedRooms: roomsRes.data.filter(r => r.status === 'OCCUPIED').length,
          availableRooms: roomsRes.data.filter(r => r.status === 'AVAILABLE').length,
          maintenanceRooms: roomsRes.data.filter(r => r.status === 'MAINTENANCE').length,
          cleaningRooms: roomsRes.data.filter(r => r.status === 'CLEANING').length,
          pendingTasks: tasksRes.data.filter(t => t.status !== 'DONE').length,
          totalReservations: reservationsRes.data.length,
        });
      } catch (e) {
        setError('Failed to load dashboard data. Some services may be down.');
        setStats({
          totalRooms: 0,
          occupiedRooms: 0,
          availableRooms: 0,
          maintenanceRooms: 0,
          cleaningRooms: 0,
          pendingTasks: 0,
          totalReservations: 0,
        });
        setReport(null);
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  return (
    <div className="container">
      <h1>Hotel Management Dashboard</h1>
      {error && <div className="error">{error}</div>}
      {loading ? (
        <div>Loading dashboard...</div>
      ) : (
        <>
          <div className="row" style={{marginBottom: 24}}>
            <div className="col card stat-card">
              <div>Total Rooms</div>
              <div className="stat-value">{stats?.totalRooms ?? 0}</div>
            </div>
            <div className="col card stat-card">
              <div>Occupied</div>
              <div className="stat-value">{stats?.occupiedRooms ?? 0}</div>
            </div>
            <div className="col card stat-card">
              <div>Available</div>
              <div className="stat-value">{stats?.availableRooms ?? 0}</div>
            </div>
            <div className="col card stat-card">
              <div>Maintenance</div>
              <div className="stat-value">{stats?.maintenanceRooms ?? 0}</div>
            </div>
            <div className="col card stat-card">
              <div>Cleaning</div>
              <div className="stat-value">{stats?.cleaningRooms ?? 0}</div>
            </div>
            <div className="col card stat-card">
              <div>Pending Tasks</div>
              <div className="stat-value">{stats?.pendingTasks ?? 0}</div>
            </div>
            <div className="col card stat-card">
              <div>Reservations</div>
              <div className="stat-value">{stats?.totalReservations ?? 0}</div>
            </div>
          </div>

          <div className="row">
            <div className="col card" style={{marginRight: 16}}>
              <h2>Rooms</h2>
              <table className="dashboard-table">
                <thead>
                  <tr>
                    <th>ID</th><th>Number</th><th>Status</th><th>Type</th><th>Floor</th><th>Amenities</th>
                  </tr>
                </thead>
                <tbody>
                  {rooms?.slice(0, 10).map(room => (
                    <tr key={room.id}>
                      <td>{room.id}</td>
                      <td>{room.number}</td>
                      <td>{room.status}</td>
                      <td>{room.type_id}</td>
                      <td>{room.floor}</td>
                      <td>{room.amenities}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {rooms && rooms.length > 10 && <div style={{fontSize:12, color:'#888'}}>Showing first 10 of {rooms.length} rooms</div>}
            </div>
            <div className="col card" style={{marginRight: 16}}>
              <h2>Reservations</h2>
              <table className="dashboard-table">
                <thead>
                  <tr>
                    <th>ID</th><th>Room</th><th>Guest</th><th>Status</th><th>Check-in</th><th>Check-out</th>
                  </tr>
                </thead>
                <tbody>
                  {reservations?.slice(0, 10).map(r => (
                    <tr key={r.id}>
                      <td>{r.id}</td>
                      <td>{r.room_id}</td>
                      <td>{r.guest_id}</td>
                      <td>{r.status}</td>
                      <td>{r.check_in}</td>
                      <td>{r.check_out}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {reservations && reservations.length > 10 && <div style={{fontSize:12, color:'#888'}}>Showing first 10 of {reservations.length} reservations</div>}
            </div>
            <div className="col card">
              <h2>Housekeeping Tasks</h2>
              <table className="dashboard-table">
                <thead>
                  <tr>
                    <th>ID</th><th>Room</th><th>Type</th><th>Status</th><th>Assigned</th><th>Scheduled</th>
                  </tr>
                </thead>
                <tbody>
                  {tasks?.slice(0, 10).map(t => (
                    <tr key={t.id}>
                      <td>{t.id}</td>
                      <td>{t.room_id}</td>
                      <td>{t.task_type}</td>
                      <td>{t.status}</td>
                      <td>{t.assigned_to}</td>
                      <td>{t.scheduled_time ? t.scheduled_time.split('T')[0] : ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {tasks && tasks.length > 10 && <div style={{fontSize:12, color:'#888'}}>Showing first 10 of {tasks.length} tasks</div>}
            </div>
          </div>

          <div className="card" style={{marginTop: 32}}>
            <h2>Occupancy Report</h2>
            {report ? (
              <ul>
                <li><b>Property ID:</b> {report.property_id}</li>
                <li><b>Total Rooms:</b> {report.total_rooms}</li>
                <li><b>Occupied Rooms:</b> {report.occupied_rooms}</li>
                <li><b>Occupancy Rate:</b> {(report.occupancy_rate * 100).toFixed(1)}%</li>
                {report.start_date && <li><b>Start Date:</b> {report.start_date}</li>}
                {report.end_date && <li><b>End Date:</b> {report.end_date}</li>}
              </ul>
            ) : <div style={{color:'#c00'}}>Occupancy report service is unavailable.</div>}
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;
