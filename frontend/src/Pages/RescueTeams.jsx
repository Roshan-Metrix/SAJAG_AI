import React, { useState } from 'react';

const TEAMS = [
  { id: 'RT-001', name: 'Butwal Rescue Unit 3', location: 'Butwal, Rupandehi', status: 'On Mission', mission: 'Flood Rescue', members: 5, lastUpdate: '10:24 AM' },
  { id: 'RT-002', name: 'Bhairawa Rescue Unit 2', location: 'Bhairawa, Rupandehi', status: 'On The Way', mission: 'Accident Rescue', members: 4, lastUpdate: '10:20 AM' },
  { id: 'RT-003', name: 'Palpa Rescue Unit 1', location: 'Palpa, Tanahun', status: 'On Mission', mission: 'Landslide Response', members: 5, lastUpdate: '10:18 AM' },
  { id: 'RT-004', name: 'Kathmandu Rescue Unit 5', location: 'Kathmandu', status: 'Available', mission: '-', members: 6, lastUpdate: '10:15 AM' },
  { id: 'RT-005', name: 'Pokhara Rescue Unit 2', location: 'Pokhara, Kaski', status: 'Standby', mission: '-', members: 4, lastUpdate: '10:10 AM' },
  { id: 'RT-006', name: 'Biratnagar Rescue Unit 1', location: 'Biratnagar, Morang', status: 'On Mission', mission: 'Fire Response', members: 5, lastUpdate: '10:08 AM' },
  { id: 'RT-007', name: 'Nepalgunj Rescue Unit 1', location: 'Nepalgunj, Banke', status: 'On The Way', mission: 'Flood Rescue', members: 5, lastUpdate: '10:05 AM' },
  { id: 'RT-008', name: 'Dhangadhi Rescue Unit 1', location: 'Dhangadhi, Kailali', status: 'Available', mission: '-', members: 4, lastUpdate: '10:02 AM' },
];

const STATUS_STYLE = {
  'On Mission': 'text-green-600 bg-green-50 font-semibold',
  'On The Way': 'text-orange-500 bg-orange-50',
  'Available': 'text-blue-600 bg-blue-50',
  'Standby': 'text-gray-500 bg-gray-100',
};

export default function RescueTeams() {
  const [search, setSearch] = useState('');

  const filtered = TEAMS.filter(t =>
    search === '' || t.name.toLowerCase().includes(search.toLowerCase()) || t.location.toLowerCase().includes(search.toLowerCase())
  );

  const counts = { total: 32, onMission: 12, onTheWay: 10, available: 8, standby: 2 };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 p-4 space-y-4 bg-[#f0f4f8]">
        {/* Stats */}
        <div className="grid grid-cols-5 gap-3">
          {[
            { label: 'Total Teams', value: counts.total, sub: 'Active across field', color: 'text-gray-800' },
            { label: 'On Mission', value: counts.onMission, sub: 'Teams currently deployed', color: 'text-green-600' },
            { label: 'On The Way', value: counts.onTheWay, sub: 'Teams en route', color: 'text-orange-500' },
            { label: 'Available', value: counts.available, sub: 'Teams ready', color: 'text-blue-600' },
            { label: 'Standby', value: counts.standby, sub: 'Teams in standby', color: 'text-yellow-600' },
          ].map(s => (
            <div key={s.label} className="bg-white rounded-xl p-4 shadow-sm">
              <p className="text-xs text-gray-500">{s.label}</p>
              <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-gray-400 mt-1">{s.sub}</p>
            </div>
          ))}
        </div>

        {/* Table */}
        <div className="bg-white rounded-xl shadow-card overflow-hidden">
          <div className="flex items-center gap-3 p-4 border-b">
            <div className="relative flex-1 max-w-xs">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🔍</span>
              <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search teams..." className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500" />
            </div>
            <button className="flex items-center gap-2 text-sm border border-gray-200 px-3 py-2 rounded-lg hover:bg-gray-50">
              ▽ Filter
            </button>
            <button className="ml-auto flex items-center gap-2 bg-[#1a3a6b] text-white text-sm px-4 py-2 rounded-lg hover:bg-[#0f2347]">
              ＋ Add Team
            </button>
          </div>
          <table className="w-full">
            <thead className="bg-[#f8fafc] border-b border-gray-100">
              <tr>
                {['Team ID','Team Name','Location','Status','Current Mission','Members','Last Update','Actions'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y">
              {filtered.map(t => (
                <tr key={t.id} className="hover:bg-gray-50 transition">
                  <td className="px-4 py-3 text-xs text-blue-600 font-medium">{t.id}</td>
                  <td className="px-4 py-3 text-xs text-gray-800 font-medium">{t.name}</td>
                  <td className="px-4 py-3 text-xs text-gray-500">{t.location}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full ${STATUS_STYLE[t.status]}`}>{t.status}</span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-600">{t.mission}</td>
                  <td className="px-4 py-3 text-xs text-gray-600">{t.members}</td>
                  <td className="px-4 py-3 text-xs text-gray-400">{t.lastUpdate}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button className="text-gray-400 hover:text-gray-600 text-sm">⋯</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50">
            <p className="text-xs text-gray-500">Showing 1 to {filtered.length} of 32 teams</p>
            <div className="flex gap-1">
              {['‹','1','2','3','4','›'].map(p => (
                <button key={p} className={`px-2.5 py-1 text-xs rounded ${p==='1'?'bg-[#1a3a6b] text-white':'text-gray-500 hover:bg-gray-100'}`}>{p}</button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
