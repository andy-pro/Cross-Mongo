/*** Model: Chain, contains chain data, links information ***/
function Chain(depth, ext) { // constructor
	this.on = function(_e, _h) {
		switch(_e) {
	    case 'change': this.hS = _h; break;	// <select> input change handler
	    case 'load': $.when.apply($, this.promises).always(function() { run(_h); }); // chain load complete handler
		}
		return this;
  }
	this.addLink = function(link) {
		link = new Link(this, link);
		this.chain[link.id] = link;
		link.row.appendTo(this.body);
		this.count++;
	}
	this.setPlint = function(oi, id, edited, ttl, pos, par, clr, det) {
		var	pre = `pairs.${id}.`, plints = this.plints;
		if (!plints[oi]) plints[oi]= {};
		plints[oi][pre+'ttl'] = ttl || '';
		plints[oi][pre+'pos'] = pos || 0;
		plints[oi][pre+'par'] = par || 0;
		plints[oi][pre+'clr'] = clr || 0;
		if (edited) plints[oi][pre+'det'] = det || '';
		//console.log('oi:', oi, 'plint:', plints[oi]);
	}
	this.order = function(ttl, det) {
		var link, oi, pos=1, self = this;
		$.each(this.body.sortable('toArray'), function() {
			link = self.chain[this.split('-')[1]];  // retrive index from id='chainId-index'
			oi = link.plint.id;
			if (oi) {  // pearl off rows with "Not crossed"
				self.setPlint(oi, link.pair.id, link.edited, ttl, pos++, link.par, link.clr, det);
			}
		});
	}
	this.stages = ['cross','vertical','plint','pair'];
	this.cache = $scope.crosses;
	this.body = $('#chainbody');
	this.plints = {};
	this.chain = {};
	this.promises = [];
	this.depth = depth || 1;
	this.ext = ext;	// extend mode, extra cols: edited, add parallel, color
	this.count = 0;
	if ($scope.chain) {
		var self = this, plints = this.plints;
		$.each($scope.chain, function() {
			self.addLink(this);
			self.setPlint(this.plintId, this.pairId, this.edited);
		});
		this.body.sortable();
		$('#addLink').click(function() { self.addLink(); });
	} else this.addLink();
}
/*** end model: Chain ***/
//===========================================================

/*** Model: Link, response <selector> sequence to row ***/
function Link(Chain, link) { // constructor
	link || (link = {});
	this.Chain = Chain;
	this.depth = Chain.depth;
	this.id = Chain.count;
	this.cross = {id: link.crossId || '', data: Chain.cache};
	this.vertical = {id: link.verticalId || ''};
	this.plint = {id: link.plintId || ''};
	this.pair = {id: link.pairId || ''};
	this.edited = link.edited;
	this.par = Boolean(link.par);
	this.clr = link.clr || 0;
	this.row = $('<tr id="%s">'.format('chainId-'+this.id));
	this.cache = [];
	var td, stage, El;
	if (Chain.ext) { this.row.addClass('move').append(this.add_td(true).html(link.edited?L.i_ok:'')); }
	for(var i = 0; i < this.depth; i++) {
		stage = Chain.stages[i];
		this[stage].El = this.add_sel().data({stage:stage}).on('change', this.selectChange);
	}
	if (Chain.ext) {
		this.title = this.add_td(true);
		this.comdata = this.add_td(true);
		this.pair['parenEl'] = $('<input type="checkbox" title="Add parallel">').prop({disabled:true, checked:this.par}).data({this:this}).on('change', this.parChange).appendTo(this.add_td(true));
		this.pair['colorEl'] = this.add_sel().on('change', colorChange).colouring(this.clrs).val(this.clr).trigger('change');
	}
	this.cross.El.append($('<option>').text(L._NOT_CROSSED_).attr('value', ''));
	this.appendOptions(this.cross);
	this.setVertical();
}

Link.prototype = {
	clrs: app.LINK_CLRS,
	add_td: function(_c) { return $(_c?'<td class="padd9">':'<td>').appendTo(this.row); },
	add_sel: function () { return $('<select class="form-control input-sm">').prop('disabled', true).data({this:this}).appendTo(this.add_td());},
	selectChange: function(event) {
		var El = $(this),
				self = El.data('this'),
				stage = El.data('stage');
		self[stage].id = El.val();
		self[stage].si = El[0].selectedIndex;
		//if (stage !== 'pair') self[stage+'Change']();  // execute crossChange(), verticalChange() or plintChange()
		self[stage+'Change']();  // execute crossChange(), verticalChange() or plintChange()
		if (typeof self.Chain.hS === 'function') {
			El = this;
			self.cache.xhr.always(function() {
				//console.log(status, 'onselect occure:', stage, self[stage]);
				self.Chain.hS.call(El, event);
			});
		}
		return false;
	},
	setVertical: function() {
		if (this.cross.id) {
			var cache = this.cross.data[this.cross.si-1];    // '-1' because row 0 is 'Not crossed'
			this.cross.title = cache[1];
			this.vertical.data = cache[2];    // shortcut to vertical data of cross from cache
			if (cache[2].length) {
				this.appendOptions(this.vertical);
				this.setPlint();
			}
		} else this.cross.title = '';
	},
	setPlint: function() {
		if (this.depth > 2) {
			if (this.vertical.id) {
				var self = this,
						cache = this.vertical.data[this.vertical.si]; // shortcut to cross[id].vertical[id]
				this.vertical.title = cache[1];
				if (!cache.xhr) {
					cache.xhr = $.get(web2spa.compose_url('plintscd', {args:[this.vertical.id]})).always(function(data, status) {
						cache[2] = status=='success' ? data.data : [[0,status,0,'']];	// data is jqXHR if error
					});
				}
				this.cache = cache;
				this.Chain.promises.push(cache.xhr);
				cache.xhr.always(function() { // add function to inner array of promise object
					if (self.cache.xhr == cache.xhr && !self.plint.data) {
						self.plint.data = cache[2];
						if (cache[2].length) {	// append plints & pairs <options>
							self.appendOptions(self.plint);
							self.plintChange(self.pair.id || '0');
						}
					}
				});
			}
		}
	},
	crossChange: function() {
		this.stageDisable(this.vertical);
		this.plintDisable();
		this.setVertical();
	},
	verticalChange: function() {
		this.plintDisable(); //----- plint, pair selectors disable
		this.setPlint();
	},
	plintChange: function(pair) {
		var plint = this.pairChange();
		this.plint.title = plint[1];
		if (this.comdata) this.comdata.html(plint[3]);
		if (this.depth > 3) {
			var El = this.pair.El,
					o = $('option', El), // get options set of select
					start = +plint[2];
			if (o.length) {  // if options exist, simply change text
				$.each(o, function (i) {this.text = i + start + (_DEBUG_ ? ' : v.'+String(i+1) : '')});
			} else {
				El.prop('disabled', false);   // if it was early cleared and disabled, append new options
				for(var i= 0; i < 10; i++) $('<option>').text(i+start + (_DEBUG_ ? ' : v.'+String(i) : '')).attr('value', i).appendTo(El);
			}
			if (pair) {
				El.val(pair);
				this.pair.id = pair;
				this.setPairProp(false);
			}
		}
	},
	pairChange: function() {
		var plint = this.plint.data[this.plint.si];
		if (this.title) this.title.html('<sup>'+plint[2]+'</sup>'+plint[4][+this.pair.id]);
		return plint;
	},
	stageDisable: function(stage) {
		stage.El.empty();
		stage.El.prop('disabled', true);
		//stage.id = 0;
		stage.id = '';
		stage.title = '';
		stage.data = null;
	},
	plintDisable: function() {  //----- plint, pair selectors disable
		if (this.depth > 2) {
			this.stageDisable(this.plint);
			if (this.title) this.title.empty();
			if (this.comdata) this.comdata.empty();
			if (this.depth > 3) {
				this.stageDisable(this.pair);
				this.setPairProp(true);
			}
		}
	},
	setPairProp: function(value) {
		if (this.Chain.ext) {
			this.pair.parenEl.prop('disabled', value);
			this.pair.colorEl.prop('disabled', value);
		}
	},
	appendOptions: function(stage) {
		var El = stage.El;
		$.each(stage.data, function() { El.append($('<option>').text(this[1]+(_DEBUG_ ? ' : '+this[0] : '')).attr('value', this[0])); });
		El.prop('disabled', false);
		if (stage.id) El.val(stage.id);
		else { El.prop('selectedIndex', 0); stage.id = El.val(); }
		stage.si = El[0].selectedIndex;
	},
	parChange: function() {
		var self = $(this).data('this');
		self.par = this.checked;
	}
}
/*** end model: Link ***/
//===========================================================

/*** Model: Cable ***/
function Cable(cable) { // constructor
	if (!(cable instanceof Array)) cable = ['', '', '', 0]
	this.row = $('<tr>');
	this.title = this.addCell(this._inp).val(cable[1]);
	this.details = this.addCell(this._inp).val(cable[2]);
	this.clr = cable[3];
	this.addCell('<select>').on('change', colorChange).colouring(this.clrs).val(this.clr).trigger('change');
	if (cable[0]) {
		this.id = cable[0];
		this.delete = $('<input type="checkbox">');
	}
	$('<td class="padd9">').append(this.delete).appendTo(this.row);
}

Cable.prototype = {
	clrs: app.CABLE_CLRS,
	_inp: '<input type="text">',
	addCell: function (El) {
		El = $(El).attr('class', 'form-control input-sm').data({this:this});
		$('<td>').append(El).appendTo(this.row);
		return El;
	}
}
/*** end model: Cable ***/
//===========================================================

/*** Model's event handlers ***/
function colorChange() {
	var self = $(this).data('this');	// get model
	self.clr = this.selectedIndex;  // get current <option>
	var _c = self.clrs[self.clr];
	$(this.parentElement.parentElement).css('background', _c);
	$(this).css('background', _c);
}
/*** end model's event handlers ***/

/*** jQuery extensions ***/
$.fn.colouring = function(_c) {
	var El = this;
	$.each(_c, function(i) { $('<option>').css('background', this).attr('value', i).appendTo(El); });
	return this;
}
