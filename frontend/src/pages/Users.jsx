import React, { useState } from 'react';

const USERS = [
  { id: 'USR-001', name: 'Inspector Sharma', role: 'Administrator', dept: 'Butwal Police Office', phone: '9841234567', status: 'Active', lastActive: '10:24 AM' },
  { id: 'USR-002', name: 'ASI Ramesh Thapa', role: 'Rescue Team', dept: 'Butwal Rescue Unit 3', phone: '9841234568', status: 'Active', lastActive: '10:18 AM' },
  { id: 'USR-003', name: 'Head Constable S. Karki', role: 'Rescue Team', dept: 'Palpa Unit 1', phone: '9812345678', status: 'Active', lastActive: '09:58 AM' },
  { id: 'USR-004', name: 'Citizen - Ram Bahadur', role: 'Citizen', dept: '-', phone: '9845678901', status: 'Active', lastActive: '09:45 AM' },
  { id: 'USR-005', name: 'Citizen - Anita Gurung', role: 'Citizen', dept: '-', phone: '9861234567', status: 'Active', lastActive: '09:30 AM' },
  { id: 'USR-006', name: 'Sub Inspector P. Oli', role: 'Rescue Team', dept: 'Lumbini Range', phone: '9859876543', status: 'Active', lastActive: '09:15 AM' },
  { id: 'USR-007', name: 'Admin - D. Adhikari', role: 'Administrator', dept: 'Control Room', phone: '9841112222', status: 'Active', lastActive: '09:05 AM' },
  { id: 'USR-008', name: 'Citizen - Suman Magar', role: 'Citizen', dept: '-', phone: '9818989898', status: 'Inactive', lastActive: '2 days ago' },
  { id: 'USR-009', name: 'Constable B. KC', role: 'Rescue Team', dept: 'Kapilvastu Unit 2', phone: '9863332211', status: 'Active', lastActive: '08:50 AM' },
  { id: 'USR-010', name: 'Officer - M. Pokharel', role: 'Administrator', dept: 'District Coordination', phone: '9844545454', status: 'Active', lastActive: '08:30 AM' },
];

const ROLE_STYLE = {
  'Administrator': 'text-purple-600 bg-purple-50',
  'Rescue Team': 'text-blue-600 bg-blue-50',
  'Citizen': 'text-green-600 bg-green-50',
};

export default function Users() {
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('All Roles');

  const filtered = USERS.filter(u =>
    (roleFilter === 'All Roles' || u.role === roleFilter) &&
    (search === '' || u.name.toLowerCase().includes(search.toLowerCase()) || u.id.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 p-4 space-y-4 bg-[#f0f4f8]">
        {/* Stats */}
        <div className="grid grid-cols-5 gap-3">
          {[
            { label: 'Total Users', value: 156, sub: '↑ 12 this month', color: 'text-gray-800' },
            { label: 'Rescue Team', value: 65, sub: '41.7%', color: 'text-blue-600' },
            { label: 'Administrators', value: 18, sub: '11.5%', color: 'text-purple-600' },
            { label: 'Citizens', value: 73, sub: '46.8%', color: 'text-green-600' },
            { label: 'Active Users', value: 142, sub: '91.0%', color: 'text-teal-600' },
          ].map(s => (
            <div key={s.label} className="bg-white rounded-xl p-4 shadow-sm">
              <p className="text-xs text-gray-500">{s.label}</p>
              <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-green-600 mt-1">{s.sub}</p>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl shadow-card overflow-hidden">
          <div className="flex items-center gap-3 p-4 border-b">
            <div className="relative flex-1 max-w-xs">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🔍</span>
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search users..." className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500" />
            </div>
            <select value={roleFilter} onChange={e => setRoleFilter(e.target.value)} className="text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white">
              {['All Roles','Administrator','Rescue Team','Citizen'].map(t => <option key={t}>{t}</option>)}
            </select>
            <select className="text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white">
              {['All Status','Active','Inactive'].map(t => <option key={t}>{t}</option>)}
            </select>
            <button className="ml-auto flex items-center gap-2 bg-[#1a3a6b] text-white text-sm px-4 py-2 rounded-lg hover:bg-[#0f2347]">
              ＋ Add User
            </button>
          </div>

          <table className="w-full">
            <thead className="bg-[#f8fafc] border-b border-gray-100">
              <tr>
                {['User ID','Name','Role','Team / Department','Phone','Status','Last Active','Actions'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y">
              {filtered.map(u => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-xs text-blue-600 font-medium">{u.id}</td>
                  <td className="px-4 py-3 text-xs font-medium text-gray-800">{u.name}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${ROLE_STYLE[u.role]}`}>{u.role}</span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">{u.dept}</td>
                  <td className="px-4 py-3 text-xs text-gray-600">{u.phone}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${u.status === 'Active' ? 'text-green-600 bg-green-50' : 'text-gray-500 bg-gray-100'}`}>{u.status}</span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-400">{u.lastActive}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button className="text-gray-400 hover:text-blue-500 text-sm">✏️</button>
                      <button className="text-gray-400 hover:text-gray-600 text-sm">⋯</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50">
            <p className="text-xs text-gray-500">Showing 1 to {filtered.length} of 156 users</p>
            <div className="flex gap-1">
              {['‹','1','2','3','…','16','›'].map(p => (
                <button key={p} className={`px-2.5 py-1 text-xs rounded ${p==='1'?'bg-[#1a3a6b] text-white':'text-gray-500 hover:bg-gray-100'}`}>{p}</button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
