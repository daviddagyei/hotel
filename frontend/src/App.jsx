import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // State for forms and results
  const [propertyId, setPropertyId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [rooms, setRooms] = useState(null);
  const [reservations, setReservations] = useState(null);
  const [tasks, setTasks] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState('');
  const [error, setError] = useState('');

  // API endpoints
  const ROOM_URL = 'http://localhost:8001/api/v1/rooms';
  const RESERVATION_URL = 'http://localhost:8002/api/v1/reservations';
  const TASK_URL = 'http://localhost:8003/api/v1/tasks';
  const REPORT_URL = 'http://localhost:8006/api/v1/reports';

  // Handlers
  const fetchRooms = async () => {
    setLoading('rooms'); setError(''); setRooms(null);
    try {
      const res = await axios.get(`${ROOM_URL}?property_id=${propertyId}`);
      setRooms(res.data);
    } catch (e) {
      setError('Failed to fetch rooms');
    } finally { setLoading(''); }
  };

  const fetchReservations = async () => {
    setLoading('reservations'); setError(''); setReservations(null);
    try {
      const params = { property_id: propertyId };
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      const res = await axios.get(RESERVATION_URL, { params });
      setReservations(res.data);
    } catch (e) {
      setError('Failed to fetch reservations');
    } finally { setLoading(''); }
  };

  const fetchTasks = async () => {
    setLoading('tasks'); setError(''); setTasks(null);
    try {
      const params = { property_id: propertyId };
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      const res = await axios.get(TASK_URL, { params });
      setTasks(res.data);
    } catch (e) {
      setError('Failed to fetch tasks');
    } finally { setLoading(''); }
  };

  const fetchReport = async () => {
    setLoading('report'); setError(''); setReport(null);
    try {
      const params = { property_id: propertyId };
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      const res = await axios.get(REPORT_URL, { params });
      setReport(res.data);
    } catch (e) {
      setError('Failed to fetch report');
    } finally { setLoading(''); }
  };

  return (
    <div className="container">
      <h1>Hotel Backend Integration Test</h1>
      <div className="form-section">
        <label>Property ID: <input value={propertyId} onChange={e => setPropertyId(e.target.value)} /></label>
        <label>Start Date: <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} /></label>
        <label>End Date: <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} /></label>
      </div>
      <div className="button-row">
        <button onClick={fetchRooms} disabled={loading}>Fetch Rooms</button>
        <button onClick={fetchReservations} disabled={loading}>Fetch Reservations</button>
        <button onClick={fetchTasks} disabled={loading}>Fetch Tasks</button>
        <button onClick={fetchReport} disabled={loading}>Fetch Report</button>
      </div>
      {error && <div className="error">{error}</div>}
      <div className="results">
        {loading === 'rooms' && <p>Loading rooms...</p>}
        {rooms && <pre><b>Rooms:</b> {JSON.stringify(rooms, null, 2)}</pre>}
        {loading === 'reservations' && <p>Loading reservations...</p>}
        {reservations && <pre><b>Reservations:</b> {JSON.stringify(reservations, null, 2)}</pre>}
        {loading === 'tasks' && <p>Loading tasks...</p>}
        {tasks && <pre><b>Tasks:</b> {JSON.stringify(tasks, null, 2)}</pre>}
        {loading === 'report' && <p>Loading report...</p>}
        {report && <pre><b>Report:</b> {JSON.stringify(report, null, 2)}</pre>}
      </div>
    </div>
  );
}

export default App;
