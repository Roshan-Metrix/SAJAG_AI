import React, { useEffect, useRef } from 'react';

const HOTSPOTS = [
  { loc: 'Kalanki', congestion: '80% (High)', speed: '15 km/h', trend: '↑ Increasing', status: 'High', update: '10:21 AM', color: 'text-red-600' },
  { loc: 'Koteshwor', congestion: '78% (High)', speed: '16 km/h', trend: '↑ Increasing', status: 'High', update: '10:20 AM', color: 'text-red-600' },
  { loc: 'Maitighar', congestion: '52% (Medium)', speed: '25 km/h', trend: '↔ Stable', status: 'Medium', update: '10:19 AM', color: 'text-orange-500' },
  { loc: 'New Baneshwor', congestion: '62% (Medium)', speed: '27 km/h', trend: '↔ Stable', status: 'Medium', update: '10:18 AM', color: 'text-orange-500' },
  { loc: 'Lagankhel', congestion: '28% (Low)', speed: '45 km/h', trend: '↓ Decreasing', status: 'Low', update: '10:17 AM', color: 'text-green-600' },
];

export default function TrafficAnalytics() {
  const mapRef = useRef(null);
  const leafletMap = useRef(null);

  useEffect(() => {
    const initMap = () => {
      if (!mapRef.current || leafletMap.current) return;
      const L = window.L;
      if (!L) return;

      const map = L.map(mapRef.current, { zoomControl: true, attributionControl: false }).setView([27.7172, 85.3240], 12);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }).addTo(map);
      leafletMap.current = map;

      // Traffic lines - simulated routes in Kathmandu
      const routes = [
        { pts: [[27.7172, 85.2800], [27.7100, 85.3050], [27.7040, 85.3200]], color: '#ef4444', w: 5 }, // High congestion
        { pts: [[27.7200, 85.3240], [27.7050, 85.3400], [27.6900, 85.3500]], color: '#ef4444', w: 4 },
        { pts: [[27.7300, 85.3000], [27.7172, 85.3240], [27.7050, 85.3300]], color: '#f59e0b', w: 4 }, // Medium
        { pts: [[27.6900, 85.3149], [27.7000, 85.3200], [27.7100, 85.3300]], color: '#22c55e', w: 3 }, // Low
        { pts: [[27.7400, 85.3600], [27.7300, 85.3400], [27.7172, 85.3240]], color: '#f59e0b', w: 3 },
      ];

      routes.forEach(r => {
        L.polyline(r.pts, { color: r.color, weight: r.w, opacity: 0.8 }).addTo(map);
      });

      // Hotspot markers
      [[27.7040, 85.2870, 'Kalanki - High'], [27.6912, 85.3502, 'Koteshwor - High'], [27.7040, 85.3240, 'Maitighar - Medium'], [27.6936, 85.3440, 'Lagankhel - Low']].forEach(([lat, lng, label]) => {
        const color = label.includes('High') ? '#ef4444' : label.includes('Medium') ? '#f59e0b' : '#22c55e';
        const icon = L.divIcon({
          className: 'custom-marker',
          html: `<div class="marker-glow" style="background:${color};box-shadow:0 0 16px 8px ${color}55, 0 0 32px 16px ${color}22;"></div>`,
          iconSize: [18, 18],
          iconAnchor: [9, 9],
        });
        L.marker([lat, lng], { icon }).bindPopup(label).addTo(map);
      });
    };

    if (window.L) initMap();
    else {
      const s = document.createElement('script');
      s.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      s.onload = initMap;
      document.head.appendChild(s);
    }

    return () => { if (leafletMap.current) { leafletMap.current.remove(); leafletMap.current = null; } };
  }, []);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 p-4 space-y-4 bg-[#f0f4f8]">
        <div className="grid grid-cols-2 gap-4">
          {/* Map */}
          <div className="bg-white rounded-xl shadow-card overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 border-b">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>📅 May 23, 2025</span>
              </div>
              <div className="flex items-center gap-3 text-xs">
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full bg-green-500 inline-block" /> Live</span>
                <button className="border px-3 py-1 rounded hover:bg-gray-50">▽ Filter</button>
              </div>
            </div>
            <div ref={mapRef} style={{ height: 320 }} />
            <div className="p-3 border-t">
              <p className="text-xs font-semibold text-gray-600 mb-2">Congestion Level</p>
              <div className="flex flex-col gap-1">
                {[['#ef4444','High (70%+)'],['#f59e0b','Medium (30–70%)'],['#22c55e','Low (<30%)']].map(([c,l]) => (
                  <div key={l} className="flex items-center gap-2 text-xs text-gray-500">
                    <span className="w-4 h-2 rounded" style={{background:c}} />
                    {l}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Stats + Hotspots */}
          <div className="space-y-3">
            <div className="grid grid-cols-4 gap-2">
              {[
                { label: 'Total Roads Monitored', value: 56, sub: 'Roads', color: 'text-gray-800' },
                { label: 'High Congestion', value: 8, sub: 'Roads', color: 'text-red-600' },
                { label: 'Medium Congestion', value: 16, sub: 'Roads', color: 'text-orange-500' },
                { label: 'Average Speed', value: '28', sub: 'km/h', color: 'text-blue-600' },
              ].map(s => (
                <div key={s.label} className="bg-white rounded-xl p-3 shadow-sm text-center">
                  <p className="text-[10px] text-gray-400">{s.label}</p>
                  <p className={`text-xl font-bold ${s.color}`}>{s.value}</p>
                  <p className="text-[10px] text-gray-400">{s.sub}</p>
                </div>
              ))}
            </div>

            <div className="bg-white rounded-xl shadow-card overflow-hidden">
              <div className="px-4 py-3 border-b flex items-center justify-between">
                <h3 className="font-semibold text-sm text-gray-800">Congestion Hotspots</h3>
                <div className="flex items-center gap-2 text-[11px]">
                  <span className="text-gray-400">Traffic Summary</span>
                </div>
              </div>
              <table className="w-full">
                <thead className="bg-[#f8fafc] border-b border-gray-100">
                  <tr>
                    {['Location','Congestion','Speed','Trend','Status','Update'].map(h => (
                      <th key={h} className="px-3 py-2 text-left text-[10px] font-semibold text-gray-500 uppercase">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {HOTSPOTS.map(h => (
                    <tr key={h.loc} className="hover:bg-gray-50">
                      <td className="px-3 py-2 text-xs font-medium text-gray-800">{h.loc}</td>
                      <td className={`px-3 py-2 text-xs font-semibold ${h.color}`}>{h.congestion}</td>
                      <td className="px-3 py-2 text-xs text-gray-600">{h.speed}</td>
                      <td className={`px-3 py-2 text-xs ${h.color}`}>{h.trend}</td>
                      <td className="px-3 py-2">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${h.status==='High'?'text-red-600 bg-red-50':h.status==='Medium'?'text-orange-500 bg-orange-50':'text-green-600 bg-green-50'}`}>{h.status}</span>
                      </td>
                      <td className="px-3 py-2 text-[10px] text-gray-400">{h.update}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
