import React, { useState } from 'react';

const CHANNELS = [
  { id: 'control-room', name: 'Control Room', lastMsg: 'Heavy rainfall expected in Butwal area. All teams be alert.', time: '10:24 AM', unread: 2, online: true, color: 'bg-blue-600' },
  { id: 'all-rescue', name: 'All Rescue Teams', lastMsg: 'Daily briefing at 8 AM tomorrow.', time: '09:10 AM', unread: 0, online: true, color: 'bg-green-600' },
  { id: 'butwal-3', name: 'Butwal Unit 3', lastMsg: 'Rescue operation completed successfully.', time: '10:18 AM', unread: 0, online: true, color: 'bg-orange-500' },
  { id: 'palpa-1', name: 'Palpa Unit 1', lastMsg: 'Landslide reported near Palpa. En route.', time: '10:25 AM', unread: 0, online: false, color: 'bg-purple-600' },
  { id: 'kapilvastu-2', name: 'Kapilvastu Unit 2', lastMsg: 'Flood water level increasing in Kapilvastu.', time: '09:20 AM', unread: 0, online: false, color: 'bg-teal-600' },
  { id: 'traffic', name: 'Traffic Control', lastMsg: 'Kalanki road is blocked. Use alternative route.', time: '08:55 AM', unread: 0, online: true, color: 'bg-yellow-600' },
  { id: 'medical', name: 'Medical Teams', lastMsg: 'Medical team on standby at City Hospital.', time: '09:40 AM', unread: 0, online: true, color: 'bg-red-600' },
  { id: 'all-channels', name: 'All Channels', lastMsg: '', time: '', unread: 0, online: true, color: 'bg-gray-600' },
];

const MESSAGES = {
  'control-room': [
    { from: 'Control Room', msg: 'Heavy rainfall expected in Butwal area. All teams be alert.', time: '10:24 AM', isOwn: false },
    { from: 'Me', msg: 'Received. We are on standby.', time: '10:24 AM', isOwn: true },
    { from: 'Palpa Unit 1', msg: 'Landslide reported near Palpa. En route.', time: '10:25 AM', isOwn: false },
    { from: 'Me', msg: 'Copy that. Moving to high alert.', time: '10:26 AM', isOwn: true },
    { from: 'Medical Teams', msg: 'Ensure all equipment is ready. Update every 30 minutes.', time: '10:27 AM', isOwn: false },
  ],
  'butwal-3': [
    { from: 'Butwal Unit 3', msg: 'Rescue operation completed successfully.', time: '10:18 AM', isOwn: false },
    { from: 'Me', msg: 'Great work. Return to base.', time: '10:19 AM', isOwn: true },
  ],
  'palpa-1': [
    { from: 'Palpa Unit 1', msg: 'Landslide reported near Palpa. En route.', time: '10:25 AM', isOwn: false },
  ],
};

export default function Communications() {
  const [activeChannel, setActiveChannel] = useState('control-room');
  const [newMsg, setNewMsg] = useState('');
  const [activeTab, setActiveTab] = useState('Messages');
  const messages = MESSAGES[activeChannel] || [];
  const channel = CHANNELS.find(c => c.id === activeChannel);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 flex p-4 gap-4 bg-[#f0f4f8]">
        {/* Left: Channels */}
        <div className="w-56 bg-white rounded-xl shadow-card flex flex-col overflow-hidden">
          <div className="p-3 border-b">
            <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Channels</p>
          </div>
          <div className="flex-1 overflow-y-auto divide-y">
            {CHANNELS.map(ch => (
              <button
                key={ch.id}
                onClick={() => setActiveChannel(ch.id)}
                className={`w-full flex items-center gap-2 px-3 py-2.5 text-left transition hover:bg-gray-50 ${activeChannel === ch.id ? 'bg-blue-50' : ''}`}
              >
                <div className={`w-8 h-8 rounded-full ${ch.color} flex items-center justify-center text-white text-xs font-bold flex-shrink-0 relative`}>
                  {ch.name.charAt(0)}
                  {ch.online && <span className="absolute bottom-0 right-0 w-2 h-2 bg-green-400 rounded-full border border-white" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-xs font-medium truncate ${activeChannel === ch.id ? 'text-blue-700' : 'text-gray-700'}`}>{ch.name}</p>
                  <p className="text-[10px] text-gray-400 truncate">{ch.lastMsg}</p>
                </div>
                {ch.unread > 0 && (
                  <span className="w-4 h-4 bg-blue-600 text-white text-[9px] rounded-full flex items-center justify-center flex-shrink-0">{ch.unread}</span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Right: Chat */}
        <div className="flex-1 bg-white rounded-xl shadow-card flex flex-col overflow-hidden">
          {/* Tabs */}
          <div className="flex items-center gap-1 px-4 pt-3 border-b flex-shrink-0">
            {['Messages','Broadcasts','Voice Messages','Announcements'].map(t => (
              <button key={t} onClick={() => setActiveTab(t)} className={`px-4 py-2 text-sm transition border-b-2 ${activeTab === t ? 'border-blue-600 text-blue-600 font-medium' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>{t}</button>
            ))}
            <div className="ml-auto flex items-center gap-2 mb-2">
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs">🔍</span>
                <input placeholder="Search messages..." className="pl-8 pr-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none" />
              </div>
              <select className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 bg-white">
                <option>All Channels</option>
              </select>
              <button className="bg-[#1a3a6b] text-white text-xs px-3 py-1.5 rounded-lg hover:bg-[#0f2347]">
                ＋ New Message
              </button>
            </div>
          </div>

          {/* Chat Header */}
          <div className="flex items-center gap-3 px-4 py-2 border-b bg-gray-50 flex-shrink-0">
            <div className={`w-8 h-8 rounded-full ${channel?.color || 'bg-blue-600'} flex items-center justify-center text-white text-xs font-bold relative`}>
              {channel?.name?.charAt(0)}
              {channel?.online && <span className="absolute bottom-0 right-0 w-2 h-2 bg-green-400 rounded-full border border-white" />}
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-800">{channel?.name}</p>
              <p className="text-[10px] text-green-500">● Online</p>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-2 ${m.isOwn ? 'flex-row-reverse' : ''}`}>
                {!m.isOwn && (
                  <div className={`w-7 h-7 rounded-full ${channel?.color || 'bg-blue-600'} flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0`}>
                    {m.from.charAt(0)}
                  </div>
                )}
                <div className={`max-w-xs ${m.isOwn ? 'items-end' : 'items-start'} flex flex-col`}>
                  {!m.isOwn && <p className="text-[10px] text-gray-500 mb-0.5">{m.from}</p>}
                  <div className={`px-3 py-2 rounded-xl text-xs ${m.isOwn ? 'bg-[#1a3a6b] text-white rounded-tr-none' : 'bg-gray-100 text-gray-700 rounded-tl-none'}`}>
                    {m.msg}
                  </div>
                  <p className="text-[9px] text-gray-400 mt-0.5">{m.time}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Input */}
          <div className="flex items-center gap-2 p-3 border-t flex-shrink-0">
            <input
              value={newMsg}
              onChange={e => setNewMsg(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && setNewMsg('')}
              placeholder="Type a message..."
              className="flex-1 text-sm border border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            />
            <button className="text-xl">😊</button>
            <button onClick={() => setNewMsg('')} className="w-9 h-9 bg-blue-600 text-white rounded-full flex items-center justify-center hover:bg-blue-700 text-sm">
              ➤
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
