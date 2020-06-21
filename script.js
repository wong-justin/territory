const itemsTable = document.getElementById("items");
const form = document.getElementById("form");
const sampleKeyBtn = document.getElementById("sample-key");
const sampleHeadersBtn = document.getElementById("sample-headers");
const sampleCoordsBtn = document.getElementById("sample-coords");
const downloadBtn = document.getElementById("download");
const loadingTxt = document.getElementById('loading');
const overlay = document.getElementById("overlay");
const tutorial = document.getElementById("tutorial-container");
const extraSection = document.getElementById("extra");
const HEADER_HEIGHT = 30;

let formHeight = form.clientHeight;
itemsTable.style.height = (formHeight-HEADER_HEIGHT) + "px";

function appendNewItem(item, colored, isNewAddr=false) {
  
  const newRow = document.createElement("tr");
  if (colored) {
    newRow.classList.add('colored');
  }
  if (isNewAddr) {
    newRow.classList.add('new');
  } else {
    item[0] = '';
    item[2] = '';
  }
  
  item.forEach(e => {
    const newCell = document.createElement("td");
    newCell.innerHTML = e;
    newRow.appendChild(newCell);
  })
  itemsTable.appendChild(newRow);
}
let sampleKey = 'sample_key_random_chars_Sgd7rG8Y';
let sampleCoords = "[[-81.161214709281936,28.655523562288536],[-81.158409118652344,28.654779794081826],[-81.1589938402176,28.652953302934318],[-81.16110742092134,28.653518200502031],[-81.160667538642883,28.654963382927086],[-81.16135418415071,28.655175215810612],[-81.161214709281936,28.655523562288536]]";
let sampleHeaders = `XHRPOSThttp://www.referenceusa.com/UsWhitePages/MapSearch/AddShape
[HTTP/1.1 200 OK 161ms]

Request URL:http://www.referenceusa.com/UsWhitePages/MapSearch/AddShape
Request Method:POST
Remote Address:199.125.10.77:80
Status Code:
200
Version:HTTP/1.1
	
Response Headers (826 B)	
Raw Headers
Request Headers (3.451 KB)	
Raw Headers
Host: www.referenceusa.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Request-Id: |pFMZe.xK6/f
Request-Context: appId=cid-v1:6f5cad55-8123-4589-8d6d-e647a71d2872
Content-Length: 370
Origin: http://www.referenceusa.com
Connection: keep-alive
Referer: http://www.referenceusa.com/UsWhitePages/Search/Custom/7d5032b8484d4ca58bfafaf7ed59c73e
Cookie: __utma=72359952.1087684208.1584920703.1587445479.1587479100.25; __utmz=72359952.1587041971.5.4.utmcsr=seminolecountyfl.gov|utmccn=(referral)|utmcmd=referral|utmcct=/departments-services/leisure-services/seminole-county-library/helpful-information-resources/referenceusa.stml; __hstc=68387854.2acfe334be5a447ec9e2781484710098.1584920703462.1587445480672.1587479100505.24; hubspotutk=2acfe334be5a447ec9e2781484710098; CurrentUser=37669; ASP.NET_SessionId=feqlkdiga5zjjuv4gtrh5cjq; .ASPXAUTH=522DE1AE5D5FF96661C2962CE39C03581D561BC10AD473067F0D0BE5C3345613507D625C2A16D6775A21EC55F164B8D82EDD1F5C2FC30AFB04E5CB97F71C754E2DBF74FFC126E34BDF5CC7293722ABB65CE96BD5BB7F362DF337E84B8F97E232FC59B9BD95F3D35BD1D0640E8B44C3554EB17E0F7619CFA6F4F2AA6C3116F5CA920F8CF9A9645CFB5F31E7444841E611035F8CF0969F7ACC26FF62A06CE8F3BD2EB3CAAD6BBAE39058CE2F60DFBB228848E77E085E38A8E57491676D89AEC0CE68DE549A5219058A25EB3551609571035CCE25C3B9434539946F33AF55F67F94BF359CBBD736072E01AD9D3A8A5668FEBFD9A7A77074688366C8A324547F1FF3EB9EEF473AEEAF899953E1EB6FC83438114353207627CD31051FB1910E904AB042A47361D20D0AE90AA1CC29095349D6409663BD5B6D28C325B325A50AD29E9D11E486271FB6F1880EC0825B9F5A7AB7157336AB667C25224B3C0168430AC5A02140A590D5A40FDD5689FD4B58893FE3807A9AAAB918FE4707D9995E5D5913E3998C1F04CE90B5013E6259A019B03772DEA156BF319C4CE7F852B5192737DFD3925AEDCB3806AA456FF853795D86A5EC9F754FA42ADC28D6DC293948B05CD2177B23C53459DA8139701CA85165C1CFA3F4B8DB7AD2D7133D6E7422845D4E8BEB0B03B348BC93A7AD; UserAuthenticated=true; TS0180d824=01065b9f5066dfc254a0278d176757b0e4daf0dae411527506e844d87d9604b53c87fca6bdf581870a21f8276e4e593c7d860908a014de0e5c915e3aac4c3d6f85c63323dea8f31ed33fa28e6e4783a4a14c617ec927e5be3e2abf7d1c71cbeefe8f8e4908a68bb29259589e3050e4a35efca883c0c25e2c805961178ad38e7a9ac9caae7c5fdd5cc6479048e518a5a1cfbc9887d178d15d8047c31f6b2da89173416ac0e1994a0f648ae952bc4b65326529fe3a45553fd1a37d42181c2a0041226f4a9faf; ASP.NET_SessionID=; LoginToken=fe091f87-1e23-44ee-b288-1955c56e21d7; TS01d981e1=01065b9f500d4de5b190477f18217b4f54ada5dd78d4da63e8170134dd576900f2f8fcea0280f61da5b9c61e2792e52f7bf725acd46650f41ff509794ccf4ba05615035d21bdcacf2b6ed321e7fa7f06d2d5e92bcea4540fde976e4bd45a5cec2b6adda959ec1011b84e4571616396aa624cd2178057aa0c0aee6e080f3cea5fcaf03d01d8e1d3c7105fd7711370b0720990f8fd9eaebe277aed27ad050a54ec9eeae4a7efe79d2a7cb4dded17dc463a1b3ee1bfc0e5d656a9501576ed96577b5b01ee23a690c545c3b6111ebf60c060fc033fcdaf; TS0180d824_77=08cfd42f6fab280070fdec51efa35f650f3858bed4d78c15a1b607a9cd89196a6645244591778f909035c381c66204d608ebc6791b8238000e8e1c3dc9808021f5dbd2796bddce607d9bae835b4e5ce763f4f9a9891fd3e07c3a3fde14fcacc3a571c0e8a8485667b29e1c01f94c0a27; CurrentUser=37669; __utmc=72359952; __hssrc=1; BIGipServerrefusa_http=2690296000.20480.0000; __utmb=72359952.15.10.1587479100; ai_session=Rz4Bj|1587479100003|1587484437069; __hssc=68387854.14.1587479100505; __utmt=1"`;

sampleKeyBtn.addEventListener("click", e => {
  e.preventDefault();
  form.requestKey.value = sampleKey;
});

sampleHeadersBtn.addEventListener("click", e => {
  e.preventDefault();
  form.headers.value = sampleHeaders;
});

sampleCoordsBtn.addEventListener("click", e => {
  e.preventDefault();
  form.coords.value = sampleCoords;
});

function initCollapsibles() {
  var collapsibles = document.getElementsByClassName("collapsible");
  var i;

  for (i = 0; i < collapsibles.length; i++) {
    collapsibles[i].addEventListener("click", function() {
      this.classList.toggle("active");
      
      var content = this.nextElementSibling;
      if (content.style.display === "block") {
        content.style.display = "none";
      } else {
        content.style.display = "block";
      }
    });
  }
}
initCollapsibles();

overlay.addEventListener("click", e => {
  if (tutorial !== e.target && !tutorial.contains(e.target)) { 
    overlay.style.display = "none";
  }
});

document.getElementById("close-instructions").addEventListener("click", e => {
  overlay.style.display = "none";
});

document.getElementById("show-instructions").addEventListener("click", e => {
  overlay.style.display = "block";
});

function disableDownload() {
  downloadBtn.disabled = true;
}

function enableDownload() {
  downloadBtn.disabled = false;  
}

disableDownload();
downloadBtn.addEventListener("click", e => {
  
  let params = {
    headers: {
      "Cache-Control": "max-age=0, no-cache, no-store, must-revalidate"
    },
    method: "GET"
  }
  
  fetch("/_download", params)
    .then(response => {
      console.log(response);
      return response.blob();
    })
    .then(data => {
      console.log(data);
    
      let filename = 'results.xlsx';
      
      var blob = new Blob([data], {type: 'xlsx'});
      if(window.navigator.msSaveOrOpenBlob) {
          window.navigator.msSaveBlob(blob, filename);
      }
      else{
          var elem = window.document.createElement('a');
          elem.href = window.URL.createObjectURL(blob);
          elem.download = filename;        
          document.body.appendChild(elem);
          elem.click();        
          document.body.removeChild(elem);
      }
  });
});

function startLoadingDisplay() {
  // let loadingTxt = document.createElement('p');
  // loadingTxt.id = 'loading';
  // loadingTxt.innerHTML = 'loading... ~5 secs / 100 results';
  // extraSection.appendChild(loadingTxt);
  loadingTxt.style.visibility = 'visible';
}

function stopLoadingDisplay() {
  
  loadingTxt.style.visibility = 'hidden';
  // extraSection.removeChild(loadingTxt);
}

function clearTable() {
//   var tds = document.getElementsByTagName('td');
//   while (tds[0]) tds[0].parentNode.removeChild(tds[0]);
  
//   var trs = document.getElementsByTagName('tr');
//   while (trs[0]) trs[0].parentNode.removeChild(trs[0]);
  
  while (itemsTable.firstChild) {
    itemsTable.firstChild.remove();
  }
  
  let th = document.createElement("th");
  th.colSpan = 3;
  th.style.height = HEADER_HEIGHT+"px";
  th.innerHTML = "Results";
  itemsTable.appendChild(th);
}

form.addEventListener("submit", e => {
  e.preventDefault();
  
  const data = {
    requestKey:form.requestKey.value,
    headers:form.headers.value,
    coords:form.coords.value
  }
  
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
    method: 'POST'
  }
  
  startLoadingDisplay();
  clearTable();
  disableDownload();
  
  fetch("/query", params)
    .then(response => response.json())
    .then(result => {
      console.log(result);
    
      stopLoadingDisplay();
    
      if (!result) {
        appendNewItem(['', 'error in results; check logs and probably get new key', '']);
      }
      else {
        enableDownload();
            
        var last = ''
        var colored = false;
        result.forEach(item => {
          if (item[0] == last) {
            appendNewItem(item, colored);
          }
          else {
            last = item[0]
            colored = !colored
            appendNewItem(item, colored, true);
          }
        });
      }
  });
});