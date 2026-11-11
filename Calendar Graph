import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';

const FedCalendar = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://www.federalreserve.gov/json/calendar.json')
      .then((res) => res.json())
      .then((data) => {
        // Map the fetched data structure to FullCalendar's required format
        // (Adjust property names like 'Title' and 'StartDate' if the endpoint keys differ)
        const formattedEvents = data.map((item, index) => ({
          id: index.toString(),
          title: item.Title || item.title || 'Fed Event',
          start: item.StartDate || item.date || item.start,
        }));
        
        setEvents(formattedEvents);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load Federal Reserve calendar:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading Federal Reserve schedule...</div>;
  }

  return (
    <div style={{ padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      <h2>Federal Reserve Schedule</h2>
      <FullCalendar
        plugins={[dayGridPlugin]}
        initialView="dayGridMonth"
        events={events}
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,dayGridWeek',
        }}
      />
    </div>
  );
};

export default FedCalendar;
