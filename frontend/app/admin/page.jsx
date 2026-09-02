'use client';
import {useEffect,useState} from 'react';
import Link from 'next/link';
import {api} from '../../lib/api';

export default function Admin(){
 const [pending,setPending]=useState([]),[user,setUser]=useState(null),[msg,setMsg]=useState('');
 const [form,setForm]=useState({title:'',description:'',resource_type:'report',year:'2026',author:'',keywords:'',expedition_id:''});
 const [file,setFile]=useState(null);
 useEffect(()=>{setUser(JSON.parse(localStorage.getItem('user')||'null')); loadPending()},[]);
 async function loadPending(){try{setPending(await api('/api/admin/pending'))}catch(e){setMsg('Please sign in as admin.')}}
 async function approve(id){await api(`/api/admin/resources/${id}/approve`,{method:'POST'});setPending(p=>p.filter(x=>x.id!==id));setMsg('Resource approved and published.');}
 async function create(e){e.preventDefault();setMsg('Creating resource...');try{
   const r=await api('/api/resources',{method:'POST',body:JSON.stringify({...form,year:Number(form.year)||null,expedition_id:form.expedition_id?Number(form.expedition_id):null})});
   if(file){const fd=new FormData();fd.append('file',file);await api(`/api/resources/${r.id}/file`,{method:'POST',body:fd});}
   setForm({title:'',description:'',resource_type:'report',year:'2026',author:'',keywords:'',expedition_id:''});setFile(null);setMsg('Resource created successfully.');loadPending();
 }catch(e){setMsg(e.message)}}
 return <main className="container section"><nav className="nav" style={{position:'static',marginBottom:35}}><Link className="brand" href="/">POLAR<span>INDIA</span></Link><div className="navlinks"><Link href="/explore">Explore</Link><button className="btn" onClick={()=>{localStorage.removeItem('token');localStorage.removeItem('user');location.href='/login'}}>Logout</button></div></nav>
 <div className="eyebrow">Admin dashboard</div><h1>Content operations</h1><p className="muted">Signed in as {user?.name||'user'} · {user?.role||''}</p>{msg&&<div className="card" style={{margin:'15px 0'}}>{msg}</div>}
 <div className="grid2">
  <form className="card" onSubmit={create}><h2>Add knowledge resource</h2><input className="input" required placeholder="Title" value={form.title} onChange={e=>setForm({...form,title:e.target.value})}/><br/><br/><textarea required placeholder="Description" value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/><br/><br/><div className="row"><select value={form.resource_type} onChange={e=>setForm({...form,resource_type:e.target.value})}><option value="report">Report</option><option value="publication">Publication</option><option value="dataset">Dataset</option><option value="education">Education</option></select><input className="input" placeholder="Year" value={form.year} onChange={e=>setForm({...form,year:e.target.value})}/></div><input className="input" placeholder="Author / institution" value={form.author} onChange={e=>setForm({...form,author:e.target.value})}/><br/><br/><input className="input" placeholder="Keywords" value={form.keywords} onChange={e=>setForm({...form,keywords:e.target.value})}/><br/><br/><input type="file" onChange={e=>setFile(e.target.files?.[0]||null)}/><br/><br/><button className="btn primary">Create & publish</button></form>
  <section><h2>Pending researcher submissions</h2>{pending.length?pending.map(r=><div className="card" key={r.id} style={{marginBottom:12}}><span className="tag">pending</span><h3>{r.title}</h3><p className="muted">{r.description}</p><button className="btn primary" onClick={()=>approve(r.id)}>Approve & publish</button></div>):<div className="card"><h3>No pending resources</h3><p className="muted">New researcher submissions appear here for review.</p></div>}</section>
 </div></main>
}
