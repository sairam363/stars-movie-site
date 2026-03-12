
async function searchMovie(){

let q=document.getElementById("movieInput").value
if(q.length<2)return

let res=await fetch(`/search_movie?q=${q}`)
let data=await res.json()

let results=document.getElementById("results")
results.innerHTML=""

data.forEach(m=>{

let div=document.createElement("div")
div.innerHTML=`<img src="${m.poster}" width="60"> ${m.title}`

div.onclick=function(){
document.getElementById("title").value=m.title
document.getElementById("poster").value=m.poster
document.getElementById("movieInput").value=m.title
results.innerHTML=""
}

results.appendChild(div)

})
}

document.addEventListener("DOMContentLoaded",()=>{
let input=document.getElementById("movieInput")
if(input) input.addEventListener("keyup",searchMovie)
})
