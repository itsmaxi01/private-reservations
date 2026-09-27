import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

let supabase, token, currentUser, watchItems = [];
const $ = (selector) => document.querySelector(selector);
const notice = (message) => { $("#notice").textContent = message || ""; };

async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, { ...options, headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}`, ...(options.headers || {}) } });
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail || "No se pudo completar la operación"); }
  return response.status === 204 ? null : response.json();
}

function el(tag, text, className) { const node = document.createElement(tag); if (text) node.textContent = text; if (className) node.className = className; return node; }
function action(label, handler) { const button = el("button", label); button.addEventListener("click", handler); return button; }

async function loadAll() {
  [currentUser, watchItems] = await Promise.all([api("/auth/me"), api("/watch-items")]);
  $("#identity").textContent = `${currentUser.display_name} · ${currentUser.role}`;
  const select = $('#reservation-form select[name="watch_item_id"]'); select.replaceChildren(...watchItems.map(item => { const option = el("option", `${item.title} · ${item.type}`); option.value = item.id; return option; }));
  const [reservations, messages] = await Promise.all([api("/reservations/upcoming"), api("/messages")]);
  renderReservations(reservations); renderWatchItems(); renderMessages(messages);
}

function renderReservations(items) {
  const root = $("#reservation-list"); root.replaceChildren();
  items.forEach(item => { const card=el("article", "", "card"), body=el("div"), title=item.type === "DATE" ? item.title : watchItems.find(x=>x.id===item.watch_item_id)?.title || "Watch"; body.append(el("strong", title), el("p", `${item.date} · ${item.time.slice(0,5)}`, "muted")); card.append(body); if(currentUser.role==="ADMIN") card.append(action("Eliminar",()=>remove(`/reservations/${item.id}`,loadAll))); root.append(card); });
  if(!items.length) root.append(el("p","Todavía no hay próximas reservaciones.","muted"));
}

function renderWatchItems() {
  const root=$("#watch-list"); root.replaceChildren();
  watchItems.forEach(item=>{ const card=el("article","","card"), body=el("div"), actions=el("div","","actions"); body.append(el("strong",item.title),el("p",`${item.type} · ${item.status}`,"muted")); actions.append(action(item.status==="PENDING"?"Marcar visto":"Marcar pendiente",()=>mutate(`/watch-items/${item.id}/status`,"PATCH",{status:item.status==="PENDING"?"WATCHED":"PENDING"},loadAll)),action("Reservar",()=>prepareWatch(item.id))); if(currentUser.role==="ADMIN") actions.append(action("Archivar",()=>mutate(`/watch-items/${item.id}/archive`,"POST",null,loadAll))); card.append(body,actions); root.append(card); });
}

function renderMessages(items) {
  const root=$("#message-list"); root.replaceChildren(); items.forEach(item=>{ const card=el("article","","card"), body=el("div"); body.append(el("p",`${item.is_pinned?"📌 ":""}${item.content}`),el("p",new Date(item.created_at).toLocaleString("es-MX"),"muted")); card.append(body); if(currentUser.role==="ADMIN") card.append(action("Eliminar",()=>remove(`/messages/${item.id}`,loadAll))); root.append(card); });
}

async function mutate(path, method, body, after) { try { notice(""); await api(path,{method,body:body?JSON.stringify(body):undefined}); await after(); } catch(error){ notice(error.message); } }
async function remove(path, after) { if(confirm("¿Confirmas esta eliminación?")) await mutate(path,"DELETE",null,after); }
function prepareWatch(id){ document.querySelector('[data-view="reservations"]').click(); const form=$("#reservation-form"); form.type.value="WATCH"; form.type.dispatchEvent(new Event("change")); form.watch_item_id.value=id; }

document.querySelectorAll("[data-view]").forEach(button=>button.addEventListener("click",()=>{ document.querySelectorAll(".view").forEach(v=>v.hidden=true); $(`#${button.dataset.view}`).hidden=false; }));
$("#reservation-form").type.addEventListener("change",event=>{ const watch=event.target.value==="WATCH"; document.querySelectorAll(".date-field").forEach(x=>x.hidden=watch); document.querySelectorAll(".watch-field").forEach(x=>x.hidden=!watch); });
$("#reservation-form").addEventListener("submit",event=>{ event.preventDefault(); const f=new FormData(event.target), type=f.get("type"), payload={type,date:f.get("date"),time:f.get("time")}; if(type==="DATE"){payload.title=f.get("title");payload.reason=f.get("reason");}else payload.watch_item_id=Number(f.get("watch_item_id")); mutate("/reservations","POST",payload,async()=>{event.target.reset();await loadAll();}); });
$("#watch-form").addEventListener("submit",event=>{event.preventDefault();const f=new FormData(event.target);mutate("/watch-items","POST",{title:f.get("title"),type:f.get("type")},async()=>{event.target.reset();await loadAll();});});
$("#message-form").addEventListener("submit",event=>{event.preventDefault();const f=new FormData(event.target);mutate("/messages","POST",{content:f.get("content"),is_pinned:f.get("is_pinned")==="on"},async()=>{event.target.reset();await loadAll();});});
$("#logout").addEventListener("click",()=>supabase.auth.signOut());
$("#login-form").addEventListener("submit",async event=>{event.preventDefault();const email=new FormData(event.target).get("email");const {error}=await supabase.auth.signInWithOtp({email,options:{shouldCreateUser:false,emailRedirectTo:location.origin}}); $("#login").querySelector("p").textContent=error?error.message:"Revisa tu correo para entrar.";});

async function applySession(session){ token=session?.access_token; $("#login").hidden=!!token; $("#app").hidden=!token; if(token){try{await loadAll();}catch(error){notice(error.message);}}else $("#identity").textContent=""; }
const config=await fetch("/api/config/public").then(r=>r.json()); supabase=createClient(config.supabaseUrl,config.supabasePublishableKey); const {data}=await supabase.auth.getSession(); await applySession(data.session); supabase.auth.onAuthStateChange((_event,session)=>applySession(session));
