/*
 * client side
 * Cross Connecting People
 * UkSATSE
 * Telecommunication Service
 * web2spa - together we go to the single page app!
 * andy-pro 2016
 */

/*** Global constants  ***/
const _DEBUG_ = false;
//const _DEBUG_ = true;
const _mypre = '<pre class="mypre">%s</pre>';

//_ = web2spa;

var app = {

	name: 'cross',
	api: 'ajax',

	LINK_CLRS:  ['#fff', '#9ff', '#f9f', '#ff9', '#aaf', '#afa', '#faa', '#bdf', '#fbd', '#dfb', '#fdb'],
	CABLE_CLRS: ['#fff', '#bff', '#fbf', '#ffb', '#ccf', '#bfc', '#fcc', '#cef', '#fce', '#efe', '#fdc'],
	/* for DEBUG */
	vars_watch: function() {
		$("#varswatch").text('Size of jQuery cache:%s, Size of window:%s'.format(Object.keys($.cache).length, Object.keys(window).length));
		//console.dir($.cache);
	},

	/* === stage hyperlink helpers === */
	A_Cross: function(_o) {
		return `${app.A}editcross/${_o.crossId.toString()}" title="${L._EDIT_CROSS_} ${_o.cross}">${_o.cross}</a>`;
	},
	A_Vertical: function(_o, x) {
		return `<a class="web2spa ${x||''}" href="${web2spa.start_path}vertical/${_o.verticalId}" title="${L._VIEW_VERT_} ${_o.vertical}">${_o.header||_o.vertical}</a>`;
	},
	A_Plint: function(_o) {
		var start1 = _o.pairId + _o.start1-1;
		return `<sup>${_o.start1}</sup>${app.A}editplint/${_o.plintId}" title="${L._EDIT_PLINT_} ${_o.plint}">${_o.plint}</a>`;
	},
	A_Pair: function(_o, title) {
		//var pair = _o.pairId + _o.start1-1,
		var hint, pair = _o.pairId + _o.start1;
		if (title) hint = `${L._CHAIN_} "${title}"`;
		else {
			title = `${L._PAIR_} ${pair}`;
			hint = `${L._EDIT_PAIR_} ${pair}`;
		}
		return `${app.A}editpair/${_o.plintId}/${_o.pairId}" title='${hint}' data-pair="1">${title}</a>`;
	},
	pairRow: function(pair, depth, colv) {
		depth = typeof depth !== 'undefined' ? depth : 4;
		var tda = [], fna = [this.A_Cross, this.A_Vertical, this.A_Plint, this.A_Pair];
		for(var i=0; i<depth; i++) tda.push((colv ? `<td class="colv${i}">` : '<td>')+fna[i](pair)+'</td>');
		return tda.join('');
	},
	/* --- stage hyperlink helpers --- */

	/* toggle helpers for pair href */
	toggle_wrap: function() {
		app.wrapMode.init(function(value) { $('table.vertical td').css('white-space', value ? 'pre-line' : 'nowrap'); }, true);
	},
	toggle_chain: function() {  // find <a> elements, store original href to custom data property and set 'onclick' handler
		$scope.a = $('a[data-pair]').each(function() { $(this).data('href', this.attributes.href.value); });
		app.chainMode.init(function(value) { $scope.a.each(function(){ this.href = $(this).data('href')+(value?'?chain=true':''); }); }, true);
	},
	toggle_ctrl: function() {
		function cmp_href()	{   // compose href for <a>: replace 'ctrl' with 'editpair' or 'chain', add/remove var 'chain'
			$.each($scope.a, function() {
				var em = app.editMode.value, cm = app.chainMode.value; // shortcuts
				this[2].href = this[0] + (em?'editpair':'chain') + this[1] + (em&&cm?'?chain=true':'');
			});
		}
		$scope.a = [];  // array for store splitting href: part1, part2, jQuery <a> elements
		$('a[data-pair]').each(function(i) { $scope.a[i] = this.attributes.href.value.split('\/ctrl\/').concat([this]); });
		app.editMode.init(cmp_href);  // set 'change editMode handler'
		app.chainMode.init(cmp_href, true);  // set 'change chainMode handler' and starting once
	},
	/* toggle helpers for pair href */

	str_editMode: function() {
		return `<label><input id="editMode" type="checkbox">${L._EDITOR_}</label>`;
	},
	D_Vertical: function(doctitle, header, search, news, vId) {
		return { // rendering object adaptor for Vertical/News Controllers View
			doctitle: doctitle,
			plints:$scope.plints,
			users:$scope.users,
			cables:$scope.cables,
			header:header,
			search:search,
			news:news,
			vId:vId
		}
	},
	chain_th: function() {
		var out = [];
		tbheaders.concat(L._DETAILS_,L._COMMON_DATA_,L.i_par).forEach(function(h) { out.push(`<th>${h}</th>`); });
		return out.join('');
	},
	chain_body: function(chain) {
		var out = [];
		chain.forEach(function(link) {
			out.push.call(out,
				`<tr style="background:${app.LINK_CLRS[link.clr]}">`,
				app.pairRow(link),
				`<td>${link.pdt}</td><td>${link.comdata}</td><td>${link.par?L.i_ok:""}</td></tr>`
			);
		});
		return out.join('');
	},
	strip_table: function() {
		$('table tr:nth-child(odd)').css('background-color', function(i, v) {
			// blacking color like rgb(rrr, ggg, bbb)
			return v.replace(/(\d+)/g, function(s, m) { return (+m/1.03).toFixed(); });
		});
	},
	db_clear: function() { if (confirm("A you sure?")) location.href = web2spa.root_path + 'cleardb'; }
};

$(function () {
    web2spa.init({	// application settings, !!! important: urls or url's parts without slashes
	app: app.name,
	api: app.api,	// 'cross/controllers/ajax.py' web2py controller for ajax requests
	json_api: true,
	lexicon: 'lexicon',	// lexicon url: 'cross/ajax/lexicon.json'
	templates: 'templates', // templates url: 'cross/static/templates.html
	//templates_json: 'templates', // templates.json url: 'cross/static/templates.json'
	_TMPLS_: false, // convert templates to JSON format, copy from console
	target: 'crosshome',	// main div for content
	post_back: true, // enable history.back() when forms are posted
	esc_back: true, // enable history.back() when 'ESC' key pressed
	mega: true, // 'controller/function' model
	set_title: true, // controller sets the document title
	routes: [
	    ['Cross', {index:true, shortcuts:true}],    // urls: 'cross/default/index', 'cross/default', 'cross'; JS controller: CrossCtrl; template: CrossTmpl, index=true means: path is empty, but controller is a string
	    ['Vertical'],	// url: 'cross/default/index/vertical'; JS controller: VerticalCtrl; template: VerticalTmpl
	    ['News', {template:'Vertical'}],
	    ['Chain'],
	    ['ViewFound'],
	    ['EditCross', {login_req:true}],    // will be redirect to login path, if not authorized
	    ['EditVertical', {login_req:true}],
	    ['EditPlint', {login_req:true}],
	    ['EditPair', {login_req:true}],
	    ['EditFound', {login_req:true}],
	    ['EditCables', {login_req:true}],
	    ['Restore', {master: true, login_req:true}],	// url: 'cross/default/restore', because master=true
	    ['User', {master: true, login_path:true}],  // url: 'cross/default/user' and this is login path pluralistically
	    ['Error', {error_path: true}]],

	beforeStart: function () {   /* callback, perform after app load & init, but before start, application setup */
	    L = web2spa.lexicon.data;   // global shorthand to lexicon
	    tbheaders = [L._CROSS_, L._VERTICAL_, L._PLINT_, L._PAIR_];
	    L._BTNOKCNSL_ = web2spa._render({templateId:'btnOkCancelTmpl'});    // helpers, inline templates for common buttons
	    L.i_ok = '<i class="glyphicon glyphicon-ok">';
	    L.i_par = '<i class="glyphicon glyphicon-random">';
	    app.A = '<a class="web2spa" href="' + web2spa.start_path; // <a> print helper
	    app.chainMode = new CheckBox('chainMode');
	    app.editMode = new CheckBox('editMode');
	    app.wrapMode = new CheckBox('wrapMode');
	    _DEBUG_ && web2spa.targetEl.before('<div id="debug" class="well"><button class="btn btn-default" onclick="vars_watch()">Watch</button><span id="varswatch"></span></div>');
	},
	beforeNavigate: function() {
	    app.chainMode.reset_handler();
	},
	afterNavigate: function() { _DEBUG_ && app.vars_watch(); }
    });
});
