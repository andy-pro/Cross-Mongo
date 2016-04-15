/*** ErrorController ***/
function ErrorCtrl() {
  document.title = L._ERROR_;
  web2spa.loadHTML();
}
/* end ErrorController */

//======================================
/*** UserController ***/
function UserCtrl() {
  document.title = L[$request.args[0]];   // login, logout, profile, change_password, register, request_reset_password
  $request.json = false;
  web2py_component(web2spa.compose_url($route.url), $route.target);	// as $.load, but provide form submit
}
/* end UserController */

//======================================
/*** CrossController ***/
function CrossCtrl() {
  web2spa.load_and_render();
}
/* end CrossController */

//======================================
/*** VerticalController ***/
function VerticalCtrl() {	// requests: #/vertical/id, #/vertical?search=search
  web2spa.load_and_render(
    function() {
      var search = $request.vars.search || '', vId, header;
      $("#master-search").val(search.unescapeHTML());
      if ($request.args[0]) { // for certain vertical view
        vId = $request.args[0];
        header = `${app.A}editvertical/${vId}" title="${L._EDIT_VERT_} ${$scope.vertical}">${$scope.header}</a>`;
      } else {    // for search results view
        vId = false;
        var h2 = `found?search=${search}">`;
        header = `${$scope.header}: ${app.A}view${h2}${L._VIEW_}</a> / ${app.A}edit${h2}${L._EDITOR_}</a>`;
      }
      return app.D_Vertical($scope.header, header, search.toLowerCase(), false, vId);
    },
    function() {
      app.strip_table();
      app.toggle_wrap();
      $userId && app.toggle_ctrl();
    }
  );
}
/* end VerticalController */

//======================================
/*** NewsController ***/
function NewsCtrl() {
  web2spa.load_and_render(
    function() { return app.D_Vertical(L._NEWS_, $scope.header, false, true, false); },
    app.strip_table
  );
}
/* end NewsController */

//======================================
/*** ChainController ***/
function ChainCtrl() {
  web2spa.load_and_render(null, app.toggle_chain);
}
/* end ChainController */

//======================================
/*** ViewFoundController ***/
function ViewFoundCtrl() {
  web2spa.load_and_render(null, app.toggle_chain);
}
/* end ViewFoundCtrl */

//======================================
/*** RestoreController ***/
function RestoreCtrl() {
  var file, title, ft = 'csv';
  if ($request.vars.merge) title = L._MERGE_DB_;
  else if ($request.vars.txt) { title = L._IMPORT_; ft = 'txt'; }
  else title = L._RESTORE_;
  web2spa.load_and_render(
    {doctitle:title, title:title, hint:`Select ${ft} file`},
    function() {
      var form = new Form();
      $('#upload').change(function (e) {
        file = e.target.files[0];
        $('#prop').text(file.size + ' bytes, last modified: ' + (file.lastModifiedDate ? file.lastModifiedDate.toLocaleDateString() : 'n/a'));
      });
    }
  );
}
/* end RestoreController */

//======================================
/*** EditCrossController ***/
function EditCrossCtrl() {
  web2spa.load_and_render(null, function() {
    var form = new Form();
  });
}
/* end EditCrossController */

//======================================
/*** EditVerticalController ***/

/* specific String helpers */
String.prototype.getCounter = function(re, i) {
  return this.replace(re, function(s,m) { return String(+m+i).frontZero(m.length); });
}
String.prototype.getComData = function(p1, p2, i) {
  return $.trim(this.getCounter(/%(\d+)/g, i)/*counters*/.replace(/%A/g, p1)/*actual common data*/.replace(/%M/g, p2))/*plint name*/;
}
/* end specific String helpers */

function EditVerticalCtrl() {

  const oldset = ["warning", "~", L._OLDPL_], newset = ["new", "+", L._NEWPL_];

  function verticalChange() {
    //var timeLoop = performance.now();
    //console.time('editvertical');
    //console.info('form inputs:', inputs);
    vertical = {plints:[], rplints:[]};
    var data = {rows:[]};
    //console.log(link);
    if (!inputs.delete) {
      $('#verttitle').text(inputs.title);
      var plintmask = inputs.plintmask, cable = '';
      if (plintmask) {
        var cnt = inputs.count;
        if (isNaN(cnt) || cnt=='' || cnt>100 || cnt<0) $('#plintCount').addClass('has-error');
        else {
          $('#plintCount').removeClass('has-error');
          var cdmask = inputs.cdmask.replace(/%C/g, link.cross.title||'').replace(/%V/g, link.vertical.title||''),
          rcdmask = inputs.cdmask.replace(/%C/g, $scope.cross).replace(/%V/g, $scope.vertical).unescapeHTML(),
          pairmask = inputs.pairmask,
          multiplint = /%\d+/.test(plintmask),    // one plint or more
          remote = link.plint.si,	// remote plint selected index
          editor = taEl.val().split('\n'),
          editor_en = editor && /%E/.test(pairmask);
          for(var i=0; i<cnt; i++) {
            //var plint = {maindata:{},pairdata:{}},
            //var plint = {pairs: []},
            var plint = {},
                title = plintmask.getCounter(/%(\d+)/g, i),   // plint title with counter
                pairbase = pairmask.getCounter(/%(\d+)/g, i),   // plint counter for pair
                set, row, cd, rcd = '', start1, rem_rec = '',
                oldplint = plintByTitle($scope.plints, title.escapeHTML());   // search in vertical by plint title
            if (oldplint) {
              set = oldset;
              cd = oldplint.comdata.unescapeHTML(); // actual common data from old plint
              start1 = inputs.start1all ? inputs.start1 : oldplint.start1;
              if (i==0) cable = oldplint.cable || '';
            } else {
              set = newset;
              cd = '';
              start1 = inputs.start1;
            }
            if (!oldplint || inputs.start1all) plint.start1 = start1;
            if (link.vertical.title && link.plint.data[remote+i]) {
              rem_rec = link.plint.data[remote+i];   // [id, title, start1, comdata]
              if (inputs.rcdreplace) {
                rcd = rcdmask.getComData(rem_rec[3], title, i);
                vertical.rplints.push({_id:rem_rec[0], comdata:rcd});
              }
              rem_rec = rem_rec[1];   // remote plint title
            }
            row = {class:set[0], hint:set[2], start1:start1, title:title.escapeHTML(), chr:set[1], cd:cdmask.getComData(cd, rem_rec, i), rcd:rcd, pairs:[]};
            plint.title = title;
            plint.comdata = row.cd;
            set = editor_en ? (editor[i] || '').split('\t')	: '';	// set of pair titles from editor
            for(var j=0; j<10; j++) {
              title = $.trim(pairbase.getCounter(/%P(\d+)/g, j).getCounter(/%D(\d+)/g, i*10+j)
              .replace(/%A/g, oldplint ? oldplint.pairs[j].unescapeHTML() : '')
              .replace(/%E/g, set[j] || ''));
              //plint.pairs.push({ttl: title});
              plint[`pairs.${j}.ttl`] = title;
              row.pairs.push(title);
            }
            data.rows.push(row);
            vertical.plints.push(plint);
            if (!multiplint) break;    // if not %counter, add only 1 plint
          }
        }
      }
      scEl.val(cable);
    }
    data.templateId = view_cd ? 'CDwatchTmpl': 'PTwatchTmpl';
    $('#watchbody').html(data.rows.length ? web2spa._render(data) : '');
    //console.timeEnd('editvertical');
    //console.log(performance.now() - timeLoop);
  }

  function plintByTitle(arr, title) { // title of plint: existing or new
    for(var o in arr) if (arr[o].title && arr[o].title == title) return arr[o];
    return 0;
  }

  function viewChange() {
    view_cd = vmEl.filter(':checked').val() == 'comdata';
    $('#watchhead').html(view_cd ? wthead_cd : wthead_pt);
    form.init();	// this trigger 'verticalChange'
  }

  function forceTab(e) {
    if (e.keyCode === 9) { // check tab key
      var start = this.selectionStart,
          target = e.target,
          value = target.value;
      target.value = value.substring(0, start) + "\t" + value.substring(this.selectionEnd);
      this.selectionStart = this.selectionEnd = start + 1;
      return false;
    }
  }

  function verticalSubmit() {
    localStorage.pairmask = inputs.pairmask;
    localStorage.cdmask = inputs.cdmask;
    $scope.formData = {};
    if (inputs.delete) $scope.formData.delete = 1;
    else {
      vertical.title = inputs.title;
      if ($('#setCable')[0].checked) {
        var cid = scEl.val(), ci = 0;
        if (cid) {
          vertical.cable = {_id: cid};
          ci = 1;
          if (vertical.plints.length && vertical.rplints.length) {
            vertical.cable.set = {details: vertical.rplints[0].comdata + ' - ' + vertical.plints[0].comdata};
          }
        }
        vertical.plints.forEach(function(p) {p.cable = ci});
        vertical.rplints.forEach(function(p) {p.cable = ci});
      }
      $scope.formData.vertical = JSON.stringify(vertical);
    }
    //console.log($scope.formData); return false;
    return form.post(); // don't send form data to 'post' handler
  }

  const _th_com_ = '<th width="14%">'+tbheaders[2]+'</th><th width="6%">+/~</th>';
  const _th_cdt_ = '<th width="40%">'+L._COMMON_DATA_+'</th><th>'+L._REM_CD_+'</th>';
  var view_cd, vertical, vmEl, scEl, taEl,
      wthead_cd = _th_com_ + _th_cdt_,   // for common data
      wthead_pt = _th_com_ + '<th width="8%">'.repeat(10),	// for pair titles
      form, inputs, link;

  web2spa.load_and_render(
    function() {
      $scope.verticalId = $request.args[0];
      if ($scope.s_plint) $scope.s_plint.mask = $scope.s_plint.title.replace(/(\d+)/, '%$1');
      else $scope.s_plint = {mask:'M%1', count:0};
      $scope.cdmask = localStorage.cdmask || '%A %C %V %M';
      $scope.pairmask = localStorage.pairmask || '%A %E';
      $scope.doctitle = $scope.header;
      return $scope;
    },
    function() {
      $('#helpbtn').click(function() { $.get(web2spa.static_path + "varhelp.html").success(function(data) { web2spa.show_msg(data, 'default', 0); }); });
      $('#editor').change(function() { if (this.checked) { taEl.show(); taEl.focus(); } else taEl.hide(); });
      vmEl = $('input[name=view]').on('change', viewChange);
      scEl = $('#cables'); // <select>
      form = new Form({submit: verticalSubmit, events: verticalChange});
      inputs = form.inputs;   // shorthand
      taEl = $('textarea').on('input', verticalChange).keydown(forceTab);
      var chain = new Chain(3, false);	// bind events below: var chain must be defined
      chain.on('change', verticalChange).on('load', function() { link = chain.chain[0]; viewChange(); });
    }
  );
}
/* end EditVerticalController */

//======================================
/*** EditPlintController ***/
function EditPlintCtrl() {

  function plintChange() {
    if (form.inputs.delete) return;
    mergechar.disabled = !form.inputs.merge;
    $('ol').attr('start', parseInt(form.inputs.start1));
  }

  function viewChange() { ta.css('display', function(i, v) { return v=='none' ? 'block' : 'none'; }); }

  var ta, form, mergechar;
  web2spa.load_and_render(null, function() {
    ta = $('textarea');
    ta[0].value = $scope.pairtitles.unescapeHTML();   // innerHTML used in templating system gives loss first empty line (\n), :-( ?
    ta[1].value = $scope.pairdetails.unescapeHTML();
    $('input[name=view]').on('change', viewChange);
    form = new Form({events: plintChange});
    mergechar = form.inputstext.filter('[name=mergechar]')[0];
    form.init();
  });
}
/* end EditPlintController */

//======================================
/*** EditPairController ***/
function EditPairCtrl() {

  function refreshWatch() {	//~~~~~~~~~~~~for debug~~~~~~~~~~~~~~
    var wt = $('#watchtable'), tr;
    wt.find('tr').remove('.refreshing');
    $.each(chain.chain, function(key, link) {
      tr = $('<tr>', {class:'refreshing'});
      $('<td>', {class:'warning'}).text(key).appendTo(tr);
      $.each(chain.stages, function() { $('<td>').text(link[this].id).appendTo(tr); });
      tr.appendTo(wt);   // id of element, without declare variable!!!
    });
    //console.log(form);
  }	//~~~~~~~~~~~~end for debug~~~~~~~~~~~~~~

  function editpairSubmit() {	// submit edit pair ctrl
    //console.info(chain);
    var title = this.title.value,
        details = this.details.value;
    if (chainMode) chain.order(title, details);
    else {
			var id = $request.args,
					pre = `pairs.${id[1]}.`,
					p = {};
			p[pre + 'ttl'] = title;
			p[pre + 'det'] = details;
	    chain = {plints:{}};
	    chain.plints[id[0]] = p;
    }
    $scope.formData = {};
    $scope.formData.plints = JSON.stringify(chain.plints);
    //console.log($scope.formData.plints); return false;
    return form.post();
  }

  var chainMode, form, chain;
  web2spa.load_and_render(null, function() {
    form = new Form({submit: editpairSubmit});
    chainMode = $scope.chain_mode;
    if (chainMode) {
      chain = new Chain(4, true);
      if (_DEBUG_) {
        web2spa.render({id:'ChainWatchTmpl', append:true});
        refreshWatch();
        chain.on('change', refreshWatch);
      }
      //debugger;
    }
    //console.info(chain);
    app.chainMode.init(function(value) {
      value = location.pathname + (value?'?chain=true':'');
      history.replaceState(null, null, value);
      web2spa.navigate(value);
    });
  });

}
/* end edit pair controller */

//======================================
/*** Edit Found Controller ***/
function EditFoundCtrl() {

  function refreshFoundTable() {
    var ftext = inputs.find.escapeHTML(),
      rtext = inputs.replace.escapeHTML(), re;
		try {
		  re = new RegExp(ftext, 'i');
			var out = '<span style="background-color: #ff6">'+(inputs.follow ? rtext : '$&')+'</span>';
		}
		catch(e) {}
    fdata.forEach(function(pair) {
      pair.cell.innerHTML = _mypre.format(pair.title.replace(re, out));
      plints[pair.plintId][`pairs.${pair.pairId}.ttl`] = pair.title.replace(re, rtext).unescapeHTML();
    });
  }

  function plints_to_pairs() {
    var lq = $request.vars.search.toLowerCase()
    $.each($scope.plints, function(key, plint) {  // convert : array of plints to array of pairs
      $.each(this.pairs, function(idx, pair) {
        var ttl = pair[0];
        if (ttl.toLowerCase().indexOf(lq) >= 0) {
          fdata.push({cross: plint.cross,
          crossId: plint.crossId,
          vertical: plint.vertical,
          verticalId: plint.verticalId,
          id: key,
          plintId: plint.id,
          plint: plint.title,
          title: ttl,
          details: pair[3],
          comdata: plint.comdata,
          pairId: idx,
          start1: plint.start1});
          if (!plints[plint.id]) plints[plint.id] = {};
        }
      });
    });
    return {doctitle:$scope.header, search:$request.vars.search, count:fdata.length};
  }

  function foundSubmit() { $scope.formData = {}; $scope.formData.plints = JSON.stringify(plints); return form.post(); }

  var fdata = [], plints = {}, form, inputs;
  web2spa.load_and_render(plints_to_pairs, function() {
    form = new Form({submit: foundSubmit, events: refreshFoundTable});    // edit found ctrl
    inputs = form.inputs;
    fdata.forEach(function(pair) {
      var row = foundtable.insertRow();
      row.insertAdjacentHTML('beforeend', app.pairRow(pair));
      pair.cell = row.insertCell();
      row.insertCell().innerHTML = pair.details;
      row.insertCell().innerHTML = pair.comdata;
    });
    form.init();
    app.toggle_chain();
  });
}
/* end edit found controller */

//======================================
/*** Edit Cables Controller ***/
function EditCablesCtrl() {

  function cablesSubmit() {
    var cables = [], cable, _c;
    cdata.forEach(function(_c) {
      title = _c.title.val();
      cable = {};
      try {
        if (_c.id) {
          cable._id = _c.id;
          if (_c.delete.is(':checked') || !title) { cable.delete = 'on'; throw false; }
          else throw true;
        } else if (title) throw true;
      } catch(e) {
        if (e) { cable.title = title; cable.details = _c.details.val(); cable.color = _c.clr; }
        cables.push(cable);
      }
    });
    $scope.formData = {};
    $scope.formData.cables = JSON.stringify(cables);
    //console.table(cables); console.log($scope.formData.cables); return false;
    return form.post();
  }

  function addCable(cable) {
    cable = new Cable(cable);
    cable.row.appendTo(tb);
    cdata.push(cable);
  }

  var form, cdata, tb;
  web2spa.load_and_render({doctitle:L._CABLES_}, function() {
    form = new Form({submit: cablesSubmit});
    cdata = [];
    tb = $('#cablebody');
    //for (var ci in $scope.cables) addCable(ci);
    $scope.cables.forEach(addCable);
    $('#addCable').click(addCable);
  });
}
/* end edit cables controller */

//======================================
/*** Ajax Live Search Controller ***/
// running at startup
(function() {

  var jqXHR, keypress = false, searchvalue = '', oldvalue = '', div = $("#livesearchout");

  function hidelive() {
    div.hide().empty();
  }

  function getPairTitles(event) {
    if (keypress) return;
    searchvalue = mastersearch.val();
    if(searchvalue.length > 2){
//console.log(searchvalue)
  if (searchvalue !== oldvalue) {
oldvalue = searchvalue;
if (jqXHR) jqXHR.abort();
  jqXHR = $.ajax(web2spa.compose_url("livesearch", {}), {
    data: {search: searchvalue},
dataFilter: function(data) { return data.escapeHTML(); },
  success: function(data){
    if (data.search.length) {
data.templateId = 'liveSearchTmpl';
  div.html(web2spa._render(data)).show();
  $("#livesearchout a").hover(
    function() { searchvalue = this.text; },    // handlerIn on mouseenter
    function() { searchvalue = mastersearch.val(); }   // handlerOut on mouseleave
);
  } else hidelive();
}
});
}
} else {
  oldvalue = searchvalue;
  hidelive();
}
}

  function submit(url) {
    var value = mastersearch.val();
    if (value.length > 2) {
      hidelive();
      web2spa.navigate(web2spa.start_path + url + '?search=' + value, {add:true});
    } else web2spa.show_msg(value + ' : ' + L._TOOSHORT_, 'danger', 5);
  }

  var mastersearch = $("#master-search")    // global input
.on('keydown', function() { keypress = true; })
.on('keyup', function(event) { keypress = false; getPairTitles(event); })
.on('input', getPairTitles)
.blur(function(event){
  oldvalue = searchvalue;
  hidelive();
  if (mastersearch.val() !== searchvalue) {
mastersearch.val(searchvalue);
setTimeout(function(){mastersearch.focus()}, 10);
  }
});

  $('#viewfound, #editfound').click(function() {
submit(this.id);
return false;
  });

  $('#livesearch').submit(function(e) {
submit('vertical');
  return false;
});

})();
/* end ajax live search controller */
