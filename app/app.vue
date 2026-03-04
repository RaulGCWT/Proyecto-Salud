<template>
  <div class="flex h-screen bg-gray-50 font-sans text-gray-900">
    
    <aside class="w-72 bg-slate-900 text-slate-300 flex flex-col shadow-2xl">
      <div class="p-6 border-b border-slate-800">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-emerald-900/20">
            SR
          </div>
          <div>
            <h1 class="text-white font-bold leading-none">SmartRest</h1>
            <span class="text-[10px] text-slate-500 uppercase tracking-widest">IoT Health System</span>
          </div>
        </div>
      </div>

      <nav class="flex-1 overflow-y-auto p-4 space-y-1">
        <p class="px-4 py-2 text-[11px] font-bold text-slate-500 uppercase">Monitorización</p>
        
        <a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800 text-white border border-slate-700">
          <span>📊</span> <span class="text-sm font-medium">Dashboard General</span>
        </a>

        <a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 hover:text-white transition-all group">
          <span class="opacity-70 group-hover:opacity-100">🛏️</span> 
          <span class="text-sm font-medium">Gestión de Colchones</span>
        </a>

        <p class="px-4 py-2 mt-6 text-[11px] font-bold text-slate-500 uppercase">Reglas y Datos</p>

        <a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 hover:text-white transition-all group">
          <span class="opacity-70 group-hover:opacity-100">⚠️</span> 
          <span class="text-sm font-medium">Alertas Activas</span>
        </a>

        <a href="#" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-slate-800 hover:text-white transition-all group">
          <span class="opacity-70 group-hover:opacity-100">📈</span> 
          <span class="text-sm font-medium">Historial de Salud</span>
        </a>
      </nav>

      <div class="p-4 bg-slate-950 border-t border-slate-800">
        <div class="flex items-center gap-3 p-2">
          <div class="w-9 h-9 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center text-xs font-bold">JD</div>
          <div class="flex-1">
            <p class="text-xs font-bold text-white">Juan Doe</p>
            <p class="text-[10px] text-slate-500 italic">Administrador</p>
          </div>
          <span class="text-xs text-emerald-500 text-[8px]">● Online</span>
        </div>
      </div>
    </aside>

    <main class="flex-1 flex flex-col overflow-hidden">
      
      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
        <h2 class="text-lg font-semibold text-gray-700 italic">Vista en tiempo real: Colchón ID-752</h2>
        <div class="flex gap-4">
          <button class="bg-gray-100 hover:bg-gray-200 p-2 rounded-lg text-sm px-4 font-medium transition">Refrescar</button>
          <button class="bg-emerald-600 hover:bg-emerald-700 text-white p-2 rounded-lg text-sm px-4 font-medium shadow-md transition">Exportar Datos</button>
        </div>
      </header>

      <section class="flex-1 overflow-y-auto p-8">
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          <div class="bg-white border-l-4 border-red-500 p-6 rounded-xl shadow-sm hover:shadow-md transition">
            <div class="flex justify-between items-start mb-4">
              <span class="text-xs font-bold text-gray-400 uppercase">Ritmo Cardíaco</span>
              <span class="bg-red-100 text-red-600 text-[10px] font-bold px-2 py-1 rounded">⚠️ ALTO</span>
            </div>
            <p class="text-3xl font-black text-gray-800 tracking-tight">112 <span class="text-sm font-normal text-gray-400">BPM</span></p>
            <p class="text-xs text-red-500 mt-2 font-medium">Excede la media (+15%)</p>
          </div>

          <div class="bg-white border-l-4 border-emerald-500 p-6 rounded-xl shadow-sm hover:shadow-md transition">
            <div class="flex justify-between items-start mb-4">
              <span class="text-xs font-bold text-gray-400 uppercase">Temp. Colchón</span>
              <span class="bg-emerald-100 text-emerald-600 text-[10px] font-bold px-2 py-1 rounded">✓ NORMAL</span>
            </div>
            <p class="text-3xl font-black text-gray-800 tracking-tight">36.4 <span class="text-sm font-normal text-gray-400">°C</span></p>
            <p class="text-xs text-gray-400 mt-2">Dentro del rango óptimo</p>
          </div>

          <div class="bg-white border-l-4 border-blue-500 p-6 rounded-xl shadow-sm hover:shadow-md transition">
            <div class="flex justify-between items-start mb-4">
              <span class="text-xs font-bold text-gray-400 uppercase">Eficiencia Sueño</span>
              <span class="text-blue-500 text-lg">🌙</span>
            </div>
            <p class="text-3xl font-black text-gray-800 tracking-tight">88 <span class="text-sm font-normal text-gray-400">%</span></p>
            <p class="text-xs text-gray-400 mt-2">Fase de sueño profundo</p>
          </div>

          <div class="bg-white border-l-4 border-slate-800 p-6 rounded-xl shadow-sm hover:shadow-md transition">
            <div class="flex justify-between items-start mb-4">
              <span class="text-xs font-bold text-gray-400 uppercase">Sensores Online</span>
              <span class="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            </div>
            <p class="text-3xl font-black text-gray-800 tracking-tight">12/12</p>
            <p class="text-xs text-gray-400 mt-2">Sincronizado hace 2s</p>
          </div>

        </div>

        <div class="mt-8 bg-white p-8 rounded-2xl shadow-sm border border-gray-100 min-h-[300px] flex flex-col items-center justify-center border-dashed text-gray-300">
          <p class="text-5xl mb-4">📉</p>
          <p class="font-medium text-gray-400 uppercase tracking-widest text-sm italic">Aquí irá el gráfico histórico de sensores</p>
        </div>

      </section>
    </main>

  </div>
</template>

<style>
/* Solo estilos globales necesarios */
body {
  margin: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>