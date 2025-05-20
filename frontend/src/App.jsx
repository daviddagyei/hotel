import { useState } from 'react';
import axios from 'axios';
import './App.css';

// Static options for dropdowns
const ROOM_STATUS_OPTIONS = ["AVAILABLE", "OCCUPIED", "MAINTENANCE", "CLEANING"];
const ROOM_TYPE_OPTIONS = [
  { id: 1, name: "Single" },
  { id: 2, name: "Double" },
  { id: 3, name: "Suite" },
];
const FLOOR_OPTIONS = ["1", "2"];
const AMENITIES_OPTIONS = [
  "WiFi,TV",
  "WiFi,TV,MiniBar",
  "WiFi,TV,Jacuzzi"
];

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
  const [editRoomId, setEditRoomId] = useState(null);
  const [editRoom, setEditRoom] = useState({});
  const [showAddRoom, setShowAddRoom] = useState(false);
  const [newRoom, setNewRoom] = useState({
    property_id: propertyId || 1,
    number: '',
    type_id: 1,
    status: 'AVAILABLE',
    floor: '1',
    amenities: 'WiFi,TV',
  });

  // Reservation edit/delete state
  const [editReservationId, setEditReservationId] = useState(null);
  const [editReservation, setEditReservation] = useState({});

  // Add reservation form state
  const [showAddReservation, setShowAddReservation] = useState(false);
  const [newReservation, setNewReservation] = useState({
    property_id: propertyId || 1,
    guest_id: '',
    room_id: '',
    check_in: '',
    check_out: '',
    price: '',
    payment_status: ''
  });

  // API endpoints
  const ROOM_URL = 'http://localhost:8001/api/v1/room-service/rooms';
  const RESERVATION_URL = 'http://localhost:8002/api/v1/reservations';
  const TASK_URL = 'http://localhost:8003/api/v1/tasks';
  const REPORT_URL = 'http://localhost:8006/api/v1/reports/occupancy';

  // Handlers
  const fetchRooms = async () => {
    if (!propertyId) {
      setError('Please enter a Property ID');
      return;
    }
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

  const handleEditClick = (room) => {
    setEditRoomId(room.id);
    setEditRoom({ ...room });
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditRoom((prev) => ({ ...prev, [name]: value }));
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setLoading('rooms'); setError('');
    try {
      await axios.patch(`${ROOM_URL}/${editRoomId}`, editRoom);
      setEditRoomId(null);
      setEditRoom({});
      fetchRooms();
    } catch (e) {
      setError('Failed to update room');
    } finally { setLoading(''); }
  };

  const handleAddRoomChange = (e) => {
    const { name, value } = e.target;
    setNewRoom((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddRoomSubmit = async (e) => {
    e.preventDefault();
    setLoading('rooms'); setError('');
    try {
      await axios.post(ROOM_URL, newRoom);
      setShowAddRoom(false);
      setNewRoom({
        property_id: propertyId || 1,
        number: '',
        type_id: 1,
        status: 'AVAILABLE',
        floor: '1',
        amenities: 'WiFi,TV',
      });
      fetchRooms();
    } catch (e) {
      setError('Failed to add room');
    } finally { setLoading(''); }
  };

  // Add delete room handler
  const handleDeleteRoom = async (roomId) => {
    if (!roomId) {
      console.warn('Attempted to delete room with undefined id');
      setError('Invalid room id for deletion');
      return;
    }
    if (!window.confirm('Are you sure you want to delete this room?')) return;
    setLoading('rooms'); setError('');
    try {
      await axios.delete(`${ROOM_URL}/${roomId}`);
      fetchRooms();
    } catch (e) {
      setError('Failed to delete room');
    } finally { setLoading(''); }
  };

  // Reservation handlers
  const handleEditReservationClick = (r) => {
    setEditReservationId(r.id);
    setEditReservation({ ...r });
  };
  const handleEditReservationChange = (e) => {
    const { name, value } = e.target;
    setEditReservation((prev) => ({ ...prev, [name]: value }));
  };
  const handleEditReservationSubmit = async (e) => {
    e.preventDefault();
    setLoading('reservations'); setError('');
    try {
      await axios.patch(`${RESERVATION_URL}/${editReservationId}`, editReservation);
      setEditReservationId(null);
      setEditReservation({});
      fetchReservations();
    } catch (e) {
      setError('Failed to update reservation');
    } finally { setLoading(''); }
  };
  const handleDeleteReservation = async (reservationId) => {
    if (!reservationId) {
      setError('Invalid reservation id for deletion');
      return;
    }
    if (!window.confirm('Are you sure you want to delete this reservation?')) return;
    setLoading('reservations'); setError('');
    try {
      await axios.delete(`${RESERVATION_URL}/${reservationId}`);
      fetchReservations();
      fetchRooms(); // Refresh room status after deletion
    } catch (e) {
      setError('Failed to delete reservation');
    } finally { setLoading(''); }
  };

  const handleAddReservationChange = (e) => {
    const { name, value } = e.target;
    setNewReservation((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddReservationSubmit = async (e) => {
    e.preventDefault();
    setLoading('reservations'); setError('');
    try {
      // Ensure check_in and check_out are in full ISO format with seconds
      const check_in = newReservation.check_in.length === 16 ? newReservation.check_in + ':00' : newReservation.check_in;
      const check_out = newReservation.check_out.length === 16 ? newReservation.check_out + ':00' : newReservation.check_out;
      const payload = { ...newReservation, check_in, check_out };
      await axios.post(RESERVATION_URL, payload);
      setShowAddReservation(false);
      setNewReservation({
        property_id: propertyId || 1,
        guest_id: '',
        room_id: '',
        check_in: '',
        check_out: '',
        price: '',
        payment_status: ''
      });
      fetchReservations();
      fetchRooms(); // Refresh room status after reservation
    } catch (e) {
      if (e.response && e.response.data && e.response.data.detail) {
        setError('Failed to add reservation: ' + e.response.data.detail);
      } else {
        setError('Failed to add reservation');
      }
    } finally { setLoading(''); }
  };

  const handlePopulateSampleData = () => {
    alert(
      'To populate sample data, run the following commands in your terminal (from the project root):\n\n' +
      'python backend/room_service/populate_sample_data.py\n' +
      'python backend/reservation_service/populate_sample_data.py\n' +
      'python backend/housekeeping_service/populate_sample_data.py\n' +
      'python backend/guest_service/populate_sample_data.py'
    );
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
        <button onClick={fetchRooms} disabled={loading || !propertyId}>Fetch Rooms</button>
        <button onClick={fetchReservations} disabled={loading}>Fetch Reservations</button>
        <button onClick={fetchTasks} disabled={loading}>Fetch Tasks</button>
        <button onClick={fetchReport} disabled={loading}>Fetch Report</button>
        <button onClick={handlePopulateSampleData} style={{background:'#e0e0e0',color:'#333'}}>Populate Sample Data</button>
      </div>
      {error && <div className="error">{error}</div>}
      <div className="results">
        {loading && <p>Loading...</p>}
        {rooms && (
          <div className="card">
            <h2>Rooms</h2>
            <button onClick={() => setShowAddRoom((v) => !v)} style={{marginBottom:8}}>{showAddRoom ? 'Cancel' : 'Add Room'}</button>
            {showAddRoom && (
              <form onSubmit={handleAddRoomSubmit} className="add-room-form">
                <input name="number" placeholder="Room Number" value={newRoom.number} onChange={handleAddRoomChange} required />
                <select name="type_id" value={newRoom.type_id} onChange={handleAddRoomChange}>
                  {ROOM_TYPE_OPTIONS.map(opt => <option key={opt.id} value={opt.id}>{opt.name}</option>)}
                </select>
                <select name="status" value={newRoom.status} onChange={handleAddRoomChange}>
                  {ROOM_STATUS_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                </select>
                <select name="floor" value={newRoom.floor} onChange={handleAddRoomChange}>
                  {FLOOR_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                </select>
                <select name="amenities" value={newRoom.amenities} onChange={handleAddRoomChange}>
                  {AMENITIES_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                </select>
                <button type="submit">Add</button>
              </form>
            )}
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Number</th><th>Status</th><th>Type</th><th>Floor</th><th>Amenities</th><th>Action</th>
                </tr>
              </thead>
              <tbody>
                {rooms.map(room => (
                  <tr key={room.id}>
                    {editRoomId === room.id ? (
                      <>
                        <td>{room.id}</td>
                        <td><input name="number" value={editRoom.number} onChange={handleEditChange} /></td>
                        <td>
                          <select name="status" value={editRoom.status} onChange={handleEditChange}>
                            {ROOM_STATUS_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                          </select>
                        </td>
                        <td>
                          <select name="type_id" value={editRoom.type_id} onChange={handleEditChange}>
                            {ROOM_TYPE_OPTIONS.map(opt => <option key={opt.id} value={opt.id}>{opt.name}</option>)}
                          </select>
                        </td>
                        <td>
                          <select name="floor" value={editRoom.floor} onChange={handleEditChange}>
                            {FLOOR_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                          </select>
                        </td>
                        <td>
                          <select name="amenities" value={editRoom.amenities} onChange={handleEditChange}>
                            {AMENITIES_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                          </select>
                        </td>
                        <td>
                          <button onClick={handleEditSubmit}>Save</button>
                          <button onClick={() => setEditRoomId(null)}>Cancel</button>
                        </td>
                      </>
                    ) : (
                      <>
                        <td>{room.id}</td>
                        <td>{room.number}</td>
                        <td>{room.status}</td>
                        <td>{ROOM_TYPE_OPTIONS.find(t => t.id === room.type_id)?.name || room.type_id}</td>
                        <td>{room.floor}</td>
                        <td>{room.amenities}</td>
                        <td>
                          <button onClick={() => handleEditClick(room)}>Edit</button>
                          <button onClick={() => handleDeleteRoom(room.id)} style={{marginLeft:4, color:'red'}} disabled={!room.id}>Delete</button>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {reservations && (
          <div className="card">
            <h2>Reservations</h2>
            <button onClick={() => setShowAddReservation(v => !v)} style={{marginBottom:8}}>{showAddReservation ? 'Cancel' : 'Add Reservation'}</button>
            {showAddReservation && (
              <form onSubmit={handleAddReservationSubmit} className="add-room-form">
                <input name="property_id" placeholder="Property ID" value={newReservation.property_id} onChange={handleAddReservationChange} required />
                <input name="guest_id" placeholder="Guest ID" value={newReservation.guest_id} onChange={handleAddReservationChange} required />
                <input name="room_id" placeholder="Room ID" value={newReservation.room_id} onChange={handleAddReservationChange} required />
                <input name="check_in" type="datetime-local" placeholder="Check-in" value={newReservation.check_in} onChange={handleAddReservationChange} required />
                <input name="check_out" type="datetime-local" placeholder="Check-out" value={newReservation.check_out} onChange={handleAddReservationChange} required />
                <input name="price" placeholder="Price" value={newReservation.price} onChange={handleAddReservationChange} />
                <input name="payment_status" placeholder="Payment Status" value={newReservation.payment_status} onChange={handleAddReservationChange} />
                <button type="submit">Add</button>
              </form>
            )}
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Room</th><th>Guest</th><th>Status</th><th>Check-in</th><th>Check-out</th><th>Action</th>
                </tr>
              </thead>
              <tbody>
                {reservations.map(r => (
                  <tr key={r.id}>
                    {editReservationId === r.id ? (
                      <>
                        <td>{r.id}</td>
                        <td><input name="room_id" value={editReservation.room_id} onChange={handleEditReservationChange} /></td>
                        <td><input name="guest_id" value={editReservation.guest_id} onChange={handleEditReservationChange} /></td>
                        <td><input name="status" value={editReservation.status} onChange={handleEditReservationChange} /></td>
                        <td><input name="check_in" value={editReservation.check_in} onChange={handleEditReservationChange} /></td>
                        <td><input name="check_out" value={editReservation.check_out} onChange={handleEditReservationChange} /></td>
                        <td>
                          <button onClick={handleEditReservationSubmit}>Save</button>
                          <button onClick={() => setEditReservationId(null)}>Cancel</button>
                        </td>
                      </>
                    ) : (
                      <>
                        <td>{r.id}</td>
                        <td>{r.room_id}</td>
                        <td>{r.guest_id}</td>
                        <td>{r.status}</td>
                        <td>{r.check_in}</td>
                        <td>{r.check_out}</td>
                        <td>
                          <button onClick={() => handleEditReservationClick(r)}>Edit</button>
                          <button onClick={() => handleDeleteReservation(r.id)} style={{marginLeft:4, color:'red'}} disabled={!r.id}>Delete</button>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {tasks && (
          <div className="card">
            <h2>Housekeeping Tasks</h2>
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Room</th><th>Type</th><th>Status</th><th>Assigned</th><th>Scheduled</th><th>Description</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map(t => (
                  <tr key={t.id}>
                    <td>{t.id}</td>
                    <td>{t.room_id}</td>
                    <td>{t.task_type}</td>
                    <td>{t.status}</td>
                    <td>{t.assigned_to}</td>
                    <td>{t.scheduled_time ? t.scheduled_time.split('T')[0] : ''}</td>
                    <td>{t.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {report && (
          <div className="card">
            <h2>Occupancy Report</h2>
            <ul>
              <li><b>Property ID:</b> {report.property_id}</li>
              <li><b>Total Rooms:</b> {report.total_rooms}</li>
              <li><b>Occupied Rooms:</b> {report.occupied_rooms}</li>
              <li><b>Occupancy Rate:</b> {(report.occupancy_rate * 100).toFixed(1)}%</li>
              {report.start_date && <li><b>Start Date:</b> {report.start_date}</li>}
              {report.end_date && <li><b>End Date:</b> {report.end_date}</li>}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
