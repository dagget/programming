<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" width="1200" height="198" onload="init(evt)" viewBox="0 0 1200 198" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<!-- Flame graph stack visualization. See https://github.com/brendangregg/FlameGraph for latest version, and http://www.brendangregg.com/flamegraphs.html for examples. -->
<!-- NOTES:  -->
<defs >
	<linearGradient id="background" y1="0" y2="1" x1="0" x2="0" >
		<stop stop-color="#eeeeee" offset="5%" />
		<stop stop-color="#eeeeb0" offset="95%" />
	</linearGradient>
</defs>
<style type="text/css">
	.func_g:hover { stroke:black; stroke-width:0.5; cursor:pointer; }
</style>
<script type="text/ecmascript">
<![CDATA[
	var details, searchbtn, matchedtxt, svg;
	function init(evt) {
		details = document.getElementById("details").firstChild;
		searchbtn = document.getElementById("search");
		matchedtxt = document.getElementById("matched");
		svg = document.getElementsByTagName("svg")[0];
		searching = 0;
	}

	// mouse-over for info
	function s(node) {		// show
		info = g_to_text(node);
		details.nodeValue = "Function: " + info;
	}
	function c() {			// clear
		details.nodeValue = ' ';
	}

	// ctrl-F for search
	window.addEventListener("keydown",function (e) {
		if (e.keyCode === 114 || (e.ctrlKey && e.keyCode === 70)) {
			e.preventDefault();
			search_prompt();
		}
	})

	// functions
	function find_child(parent, name, attr) {
		var children = parent.childNodes;
		for (var i=0; i<children.length;i++) {
			if (children[i].tagName == name)
				return (attr != undefined) ? children[i].attributes[attr].value : children[i];
		}
		return;
	}
	function orig_save(e, attr, val) {
		if (e.attributes["_orig_"+attr] != undefined) return;
		if (e.attributes[attr] == undefined) return;
		if (val == undefined) val = e.attributes[attr].value;
		e.setAttribute("_orig_"+attr, val);
	}
	function orig_load(e, attr) {
		if (e.attributes["_orig_"+attr] == undefined) return;
		e.attributes[attr].value = e.attributes["_orig_"+attr].value;
		e.removeAttribute("_orig_"+attr);
	}
	function g_to_text(e) {
		var text = find_child(e, "title").firstChild.nodeValue;
		return (text)
	}
	function g_to_func(e) {
		var func = g_to_text(e);
		// if there's any manipulation we want to do to the function
		// name before it's searched, do it here before returning.
		return (func);
	}
	function update_text(e) {
		var r = find_child(e, "rect");
		var t = find_child(e, "text");
		var w = parseFloat(r.attributes["width"].value) -3;
		var txt = find_child(e, "title").textContent.replace(/\([^(]*\)$/,"");
		t.attributes["x"].value = parseFloat(r.attributes["x"].value) +3;

		// Smaller than this size won't fit anything
		if (w < 2*12*0.59) {
			t.textContent = "";
			return;
		}

		t.textContent = txt;
		// Fit in full text width
		if (/^ *$/.test(txt) || t.getSubStringLength(0, txt.length) < w)
			return;

		for (var x=txt.length-2; x>0; x--) {
			if (t.getSubStringLength(0, x+2) <= w) {
				t.textContent = txt.substring(0,x) + "..";
				return;
			}
		}
		t.textContent = "";
	}

	// zoom
	function zoom_reset(e) {
		if (e.attributes != undefined) {
			orig_load(e, "x");
			orig_load(e, "width");
		}
		if (e.childNodes == undefined) return;
		for(var i=0, c=e.childNodes; i<c.length; i++) {
			zoom_reset(c[i]);
		}
	}
	function zoom_child(e, x, ratio) {
		if (e.attributes != undefined) {
			if (e.attributes["x"] != undefined) {
				orig_save(e, "x");
				e.attributes["x"].value = (parseFloat(e.attributes["x"].value) - x - 10) * ratio + 10;
				if(e.tagName == "text") e.attributes["x"].value = find_child(e.parentNode, "rect", "x") + 3;
			}
			if (e.attributes["width"] != undefined) {
				orig_save(e, "width");
				e.attributes["width"].value = parseFloat(e.attributes["width"].value) * ratio;
			}
		}

		if (e.childNodes == undefined) return;
		for(var i=0, c=e.childNodes; i<c.length; i++) {
			zoom_child(c[i], x-10, ratio);
		}
	}
	function zoom_parent(e) {
		if (e.attributes) {
			if (e.attributes["x"] != undefined) {
				orig_save(e, "x");
				e.attributes["x"].value = 10;
			}
			if (e.attributes["width"] != undefined) {
				orig_save(e, "width");
				e.attributes["width"].value = parseInt(svg.width.baseVal.value) - (10*2);
			}
		}
		if (e.childNodes == undefined) return;
		for(var i=0, c=e.childNodes; i<c.length; i++) {
			zoom_parent(c[i]);
		}
	}
	function zoom(node) {
		var attr = find_child(node, "rect").attributes;
		var width = parseFloat(attr["width"].value);
		var xmin = parseFloat(attr["x"].value);
		var xmax = parseFloat(xmin + width);
		var ymin = parseFloat(attr["y"].value);
		var ratio = (svg.width.baseVal.value - 2*10) / width;

		// XXX: Workaround for JavaScript float issues (fix me)
		var fudge = 0.0001;

		var unzoombtn = document.getElementById("unzoom");
		unzoombtn.style["opacity"] = "1.0";

		var el = document.getElementsByTagName("g");
		for(var i=0;i<el.length;i++){
			var e = el[i];
			var a = find_child(e, "rect").attributes;
			var ex = parseFloat(a["x"].value);
			var ew = parseFloat(a["width"].value);
			// Is it an ancestor
			if (0 == 0) {
				var upstack = parseFloat(a["y"].value) > ymin;
			} else {
				var upstack = parseFloat(a["y"].value) < ymin;
			}
			if (upstack) {
				// Direct ancestor
				if (ex <= xmin && (ex+ew+fudge) >= xmax) {
					e.style["opacity"] = "0.5";
					zoom_parent(e);
					e.onclick = function(e){unzoom(); zoom(this);};
					update_text(e);
				}
				// not in current path
				else
					e.style["display"] = "none";
			}
			// Children maybe
			else {
				// no common path
				if (ex < xmin || ex + fudge >= xmax) {
					e.style["display"] = "none";
				}
				else {
					zoom_child(e, xmin, ratio);
					e.onclick = function(e){zoom(this);};
					update_text(e);
				}
			}
		}
	}
	function unzoom() {
		var unzoombtn = document.getElementById("unzoom");
		unzoombtn.style["opacity"] = "0.0";

		var el = document.getElementsByTagName("g");
		for(i=0;i<el.length;i++) {
			el[i].style["display"] = "block";
			el[i].style["opacity"] = "1";
			zoom_reset(el[i]);
			update_text(el[i]);
		}
	}

	// search
	function reset_search() {
		var el = document.getElementsByTagName("rect");
		for (var i=0; i < el.length; i++) {
			orig_load(el[i], "fill")
		}
	}
	function search_prompt() {
		if (!searching) {
			var term = prompt("Enter a search term (regexp " +
			    "allowed, eg: ^ext4_)", "");
			if (term != null) {
				search(term)
			}
		} else {
			reset_search();
			searching = 0;
			searchbtn.style["opacity"] = "0.1";
			searchbtn.firstChild.nodeValue = "Search"
			matchedtxt.style["opacity"] = "0.0";
			matchedtxt.firstChild.nodeValue = ""
		}
	}
	function search(term) {
		var re = new RegExp(term);
		var el = document.getElementsByTagName("g");
		var matches = new Object();
		var maxwidth = 0;
		for (var i = 0; i < el.length; i++) {
			var e = el[i];
			if (e.attributes["class"].value != "func_g")
				continue;
			var func = g_to_func(e);
			var rect = find_child(e, "rect");
			if (rect == null) {
				// the rect might be wrapped in an anchor
				// if nameattr href is being used
				if (rect = find_child(e, "a")) {
				    rect = find_child(r, "rect");
				}
			}
			if (func == null || rect == null)
				continue;

			// Save max width. Only works as we have a root frame
			var w = parseFloat(rect.attributes["width"].value);
			if (w > maxwidth)
				maxwidth = w;

			if (func.match(re)) {
				// highlight
				var x = parseFloat(rect.attributes["x"].value);
				orig_save(rect, "fill");
				rect.attributes["fill"].value =
				    "rgb(230,0,230)";

				// remember matches
				if (matches[x] == undefined) {
					matches[x] = w;
				} else {
					if (w > matches[x]) {
						// overwrite with parent
						matches[x] = w;
					}
				}
				searching = 1;
			}
		}
		if (!searching)
			return;

		searchbtn.style["opacity"] = "1.0";
		searchbtn.firstChild.nodeValue = "Reset Search"

		// calculate percent matched, excluding vertical overlap
		var count = 0;
		var lastx = -1;
		var lastw = 0;
		var keys = Array();
		for (k in matches) {
			if (matches.hasOwnProperty(k))
				keys.push(k);
		}
		// sort the matched frames by their x location
		// ascending, then width descending
		keys.sort(function(a, b){
			return a - b;
		});
		// Step through frames saving only the biggest bottom-up frames
		// thanks to the sort order. This relies on the tree property
		// where children are always smaller than their parents.
		var fudge = 0.0001;	// JavaScript floating point
		for (var k in keys) {
			var x = parseFloat(keys[k]);
			var w = matches[keys[k]];
			if (x >= lastx + lastw - fudge) {
				count += w;
				lastx = x;
				lastw = w;
			}
		}
		// display matched percent
		matchedtxt.style["opacity"] = "1.0";
		pct = 100 * count / maxwidth;
		if (pct == 100)
			pct = "100"
		else
			pct = pct.toFixed(1)
		matchedtxt.firstChild.nodeValue = "Matched: " + pct + "%";
	}
	function searchover(e) {
		searchbtn.style["opacity"] = "1.0";
	}
	function searchout(e) {
		if (searching) {
			searchbtn.style["opacity"] = "1.0";
		} else {
			searchbtn.style["opacity"] = "0.1";
		}
	}
]]>
</script>
<rect x="0.0" y="0" width="1200.0" height="198.0" fill="url(#background)"  />
<text text-anchor="middle" x="600.00" y="24" font-size="17" font-family="Verdana" fill="rgb(0,0,0)"  >cargo test test_factors_include_large_prime -- --ignored</text>
<text text-anchor="" x="10.00" y="181" font-size="12" font-family="Verdana" fill="rgb(0,0,0)" id="details" > </text>
<text text-anchor="" x="10.00" y="24" font-size="12" font-family="Verdana" fill="rgb(0,0,0)" id="unzoom" onclick="unzoom()" style="opacity:0.0;cursor:pointer" >Reset Zoom</text>
<text text-anchor="" x="1090.00" y="24" font-size="12" font-family="Verdana" fill="rgb(0,0,0)" id="search" onmouseover="searchover()" onmouseout="searchout()" onclick="search_prompt()" style="opacity:0.1;cursor:pointer" >Search</text>
<text text-anchor="" x="1090.00" y="181" font-size="12" font-family="Verdana" fill="rgb(0,0,0)" id="matched" > </text>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>malloc (2 samples, 0.22%)</title><rect x="117.3" y="117" width="2.6" height="15.0" fill="rgb(206,175,50)" rx="2" ry="2" />
<text text-anchor="" x="120.27" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>dl_main (6 samples, 0.66%)</title><rect x="39.7" y="85" width="7.8" height="15.0" fill="rgb(210,37,50)" rx="2" ry="2" />
<text text-anchor="" x="42.73" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::num::ptr_try_from_impls::&lt;impl core::convert::TryFrom&lt;usize&gt; for u64&gt;::try_from (7 samples, 0.77%)</title><rect x="758.3" y="101" width="9.1" height="15.0" fill="rgb(244,77,37)" rx="2" ry="2" />
<text text-anchor="" x="761.32" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__read_nocancel (1 samples, 0.11%)</title><rect x="139.2" y="101" width="1.3" height="15.0" fill="rgb(229,60,37)" rx="2" ry="2" />
<text text-anchor="" x="142.24" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>mprotect (1 samples, 0.11%)</title><rect x="167.7" y="69" width="1.3" height="15.0" fill="rgb(249,105,53)" rx="2" ry="2" />
<text text-anchor="" x="170.68" y="79.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>&lt;core::iter::adapters::Cloned&lt;I&gt; as core::iter::traits::iterator::Iterator&gt;::fold (1 samples, 0.11%)</title><rect x="19.0" y="85" width="1.3" height="15.0" fill="rgb(230,33,29)" rx="2" ry="2" />
<text text-anchor="" x="22.05" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_dl_map_object (2 samples, 0.22%)</title><rect x="147.0" y="117" width="2.6" height="15.0" fill="rgb(205,182,41)" rx="2" ry="2" />
<text text-anchor="" x="150.00" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>term::terminfo::parser::compiled::read_le_u16 (1 samples, 0.11%)</title><rect x="162.5" y="117" width="1.3" height="15.0" fill="rgb(251,139,33)" rx="2" ry="2" />
<text text-anchor="" x="165.51" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__clone (21 samples, 2.30%)</title><rect x="59.1" y="117" width="27.2" height="15.0" fill="rgb(220,82,23)" rx="2" ry="2" />
<text text-anchor="" x="62.11" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >_..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>regex::compile::Compiler::fill (1 samples, 0.11%)</title><rect x="122.4" y="117" width="1.3" height="15.0" fill="rgb(231,140,19)" rx="2" ry="2" />
<text text-anchor="" x="125.44" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>mmap64 (1 samples, 0.11%)</title><rect x="184.5" y="117" width="1.3" height="15.0" fill="rgb(229,123,38)" rx="2" ry="2" />
<text text-anchor="" x="187.48" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>memcpy@GLIBC_2.2.5 (5 samples, 0.55%)</title><rect x="957.4" y="101" width="6.4" height="15.0" fill="rgb(240,84,26)" rx="2" ry="2" />
<text text-anchor="" x="960.36" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[unknown] (1 samples, 0.11%)</title><rect x="20.3" y="53" width="1.3" height="15.0" fill="rgb(235,178,33)" rx="2" ry="2" />
<text text-anchor="" x="23.34" y="63.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::cmp::impls::&lt;impl core::cmp::PartialOrd for u64&gt;::lt (11 samples, 1.20%)</title><rect x="258.1" y="101" width="14.3" height="15.0" fill="rgb(214,128,18)" rx="2" ry="2" />
<text text-anchor="" x="261.15" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__rust_maybe_catch_panic (775 samples, 84.88%)</title><rect x="187.1" y="117" width="1001.6" height="15.0" fill="rgb(208,166,11)" rx="2" ry="2" />
<text text-anchor="" x="190.06" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >__rust_maybe_catch_panic</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>OPENSSL_LH_insert (1 samples, 0.11%)</title><rect x="17.8" y="101" width="1.2" height="15.0" fill="rgb(207,208,23)" rx="2" ry="2" />
<text text-anchor="" x="20.75" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__read_nocancel (1 samples, 0.11%)</title><rect x="165.1" y="101" width="1.3" height="15.0" fill="rgb(221,8,41)" rx="2" ry="2" />
<text text-anchor="" x="168.09" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_dl_map_object_from_fd (1 samples, 0.11%)</title><rect x="171.6" y="101" width="1.2" height="15.0" fill="rgb(233,118,1)" rx="2" ry="2" />
<text text-anchor="" x="174.56" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__memmove_sse2_unaligned_erms (25 samples, 2.74%)</title><rect x="225.8" y="101" width="32.3" height="15.0" fill="rgb(229,98,7)" rx="2" ry="2" />
<text text-anchor="" x="228.84" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >__..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__mprotect (1 samples, 0.11%)</title><rect x="87.5" y="117" width="1.3" height="15.0" fill="rgb(237,129,3)" rx="2" ry="2" />
<text text-anchor="" x="90.55" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__GI___libc_sigaction (3 samples, 0.33%)</title><rect x="79.8" y="101" width="3.9" height="15.0" fill="rgb(247,140,32)" rx="2" ry="2" />
<text text-anchor="" x="82.79" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_dl_sysdep_start (6 samples, 0.66%)</title><rect x="39.7" y="101" width="7.8" height="15.0" fill="rgb(235,66,50)" rx="2" ry="2" />
<text text-anchor="" x="42.73" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_dl_map_object (3 samples, 0.33%)</title><rect x="92.7" y="117" width="3.9" height="15.0" fill="rgb(250,180,21)" rx="2" ry="2" />
<text text-anchor="" x="95.72" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>time (1 samples, 0.11%)</title><rect x="46.2" y="69" width="1.3" height="15.0" fill="rgb(224,56,48)" rx="2" ry="2" />
<text text-anchor="" x="49.19" y="79.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__GI___open64_nocancel (1 samples, 0.11%)</title><rect x="172.8" y="85" width="1.3" height="15.0" fill="rgb(210,107,40)" rx="2" ry="2" />
<text text-anchor="" x="175.85" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>prime_factors-d (17 samples, 1.86%)</title><rect x="163.8" y="133" width="22.0" height="15.0" fill="rgb(221,106,34)" rx="2" ry="2" />
<text text-anchor="" x="166.80" y="143.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >p..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__mmap (1 samples, 0.11%)</title><rect x="145.7" y="117" width="1.3" height="15.0" fill="rgb(222,50,24)" rx="2" ry="2" />
<text text-anchor="" x="148.71" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[unknown] (3 samples, 0.33%)</title><rect x="12.6" y="101" width="3.9" height="15.0" fill="rgb(217,229,34)" rx="2" ry="2" />
<text text-anchor="" x="15.58" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[unknown] (8 samples, 0.88%)</title><rect x="20.3" y="85" width="10.4" height="15.0" fill="rgb(236,2,1)" rx="2" ry="2" />
<text text-anchor="" x="23.34" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__clone (7 samples, 0.77%)</title><rect x="21.6" y="53" width="9.1" height="15.0" fill="rgb(214,136,53)" rx="2" ry="2" />
<text text-anchor="" x="24.63" y="63.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>test_factors_in (777 samples, 85.10%)</title><rect x="185.8" y="133" width="1004.2" height="15.0" fill="rgb(224,17,7)" rx="2" ry="2" />
<text text-anchor="" x="188.77" y="143.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >test_factors_in</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>cargo (92 samples, 10.08%)</title><rect x="10.0" y="133" width="118.9" height="15.0" fill="rgb(221,192,20)" rx="2" ry="2" />
<text text-anchor="" x="13.00" y="143.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >cargo</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>&lt;u64 as core::iter::range::Step&gt;::add_usize (25 samples, 2.74%)</title><rect x="188.4" y="101" width="32.3" height="15.0" fill="rgb(211,62,17)" rx="2" ry="2" />
<text text-anchor="" x="191.36" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >&lt;u..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__rpc_thread_destroy (1 samples, 0.11%)</title><rect x="185.8" y="117" width="1.3" height="15.0" fill="rgb(219,52,13)" rx="2" ry="2" />
<text text-anchor="" x="188.77" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_dl_sysdep_start (2 samples, 0.22%)</title><rect x="141.8" y="101" width="2.6" height="15.0" fill="rgb(249,142,10)" rx="2" ry="2" />
<text text-anchor="" x="144.83" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[unknown] (8 samples, 0.88%)</title><rect x="20.3" y="69" width="10.4" height="15.0" fill="rgb(234,81,10)" rx="2" ry="2" />
<text text-anchor="" x="23.34" y="79.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>mprotect (1 samples, 0.11%)</title><rect x="92.7" y="101" width="1.3" height="15.0" fill="rgb(254,204,30)" rx="2" ry="2" />
<text text-anchor="" x="95.72" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__GI___tunables_init (1 samples, 0.11%)</title><rect x="57.8" y="117" width="1.3" height="15.0" fill="rgb(232,1,27)" rx="2" ry="2" />
<text text-anchor="" x="60.82" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>regex::compile::Compiler::push_compiled (2 samples, 0.22%)</title><rect x="123.7" y="117" width="2.6" height="15.0" fill="rgb(215,122,12)" rx="2" ry="2" />
<text text-anchor="" x="126.73" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::mem::swap (13 samples, 1.42%)</title><rect x="448.1" y="101" width="16.8" height="15.0" fill="rgb(246,159,47)" rx="2" ry="2" />
<text text-anchor="" x="451.14" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::ptr::read (94 samples, 10.30%)</title><rect x="768.7" y="101" width="121.5" height="15.0" fill="rgb(253,43,46)" rx="2" ry="2" />
<text text-anchor="" x="771.66" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >core::ptr::read</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>&lt;clap::args::arg_builder::option::OptBuilder as core::convert::From&lt;clap::args::arg::Arg&gt;&gt;::from (1 samples, 0.11%)</title><rect x="32.0" y="69" width="1.3" height="15.0" fill="rgb(217,23,20)" rx="2" ry="2" />
<text text-anchor="" x="34.97" y="79.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>mprotect (1 samples, 0.11%)</title><rect x="44.9" y="69" width="1.3" height="15.0" fill="rgb(241,36,45)" rx="2" ry="2" />
<text text-anchor="" x="47.90" y="79.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>do_lookup_x (1 samples, 0.11%)</title><rect x="159.9" y="117" width="1.3" height="15.0" fill="rgb(254,17,26)" rx="2" ry="2" />
<text text-anchor="" x="162.92" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>all (913 samples, 100%)</title><rect x="10.0" y="149" width="1180.0" height="15.0" fill="rgb(224,123,17)" rx="2" ry="2" />
<text text-anchor="" x="13.00" y="159.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>term::terminfo::parser::compiled::parse (1 samples, 0.11%)</title><rect x="170.3" y="101" width="1.3" height="15.0" fill="rgb(212,139,17)" rx="2" ry="2" />
<text text-anchor="" x="173.26" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__GI___sigaltstack (1 samples, 0.11%)</title><rect x="56.5" y="117" width="1.3" height="15.0" fill="rgb(230,139,40)" rx="2" ry="2" />
<text text-anchor="" x="59.53" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>strlen (1 samples, 0.11%)</title><rect x="169.0" y="101" width="1.3" height="15.0" fill="rgb(211,101,2)" rx="2" ry="2" />
<text text-anchor="" x="171.97" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[unknown] (11 samples, 1.20%)</title><rect x="19.0" y="101" width="14.3" height="15.0" fill="rgb(233,102,25)" rx="2" ry="2" />
<text text-anchor="" x="22.05" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>open_path (2 samples, 0.22%)</title><rect x="94.0" y="101" width="2.6" height="15.0" fill="rgb(247,83,24)" rx="2" ry="2" />
<text text-anchor="" x="97.01" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::intrinsics::copy_nonoverlapping (60 samples, 6.57%)</title><rect x="272.4" y="101" width="77.5" height="15.0" fill="rgb(250,172,15)" rx="2" ry="2" />
<text text-anchor="" x="275.37" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >core::in..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>ssl_cipher_apply_rule (1 samples, 0.11%)</title><rect x="15.2" y="69" width="1.3" height="15.0" fill="rgb(208,37,12)" rx="2" ry="2" />
<text text-anchor="" x="18.17" y="79.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::ptr::write (8 samples, 0.88%)</title><rect x="947.0" y="101" width="10.4" height="15.0" fill="rgb(221,211,16)" rx="2" ry="2" />
<text text-anchor="" x="950.02" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>main (1 samples, 0.11%)</title><rect x="52.7" y="101" width="1.2" height="15.0" fill="rgb(227,99,16)" rx="2" ry="2" />
<text text-anchor="" x="55.65" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[prime_factors-0c57f703e6b2f430] (4 samples, 0.44%)</title><rect x="220.7" y="101" width="5.1" height="15.0" fill="rgb(229,29,12)" rx="2" ry="2" />
<text text-anchor="" x="223.67" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::option::Option&lt;T&gt;::is_none (1 samples, 0.11%)</title><rect x="767.4" y="101" width="1.3" height="15.0" fill="rgb(238,102,27)" rx="2" ry="2" />
<text text-anchor="" x="770.37" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>regex::compile::Compiler::compile_finish (1 samples, 0.11%)</title><rect x="53.9" y="101" width="1.3" height="15.0" fill="rgb(230,213,1)" rx="2" ry="2" />
<text text-anchor="" x="56.94" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__clone (8 samples, 0.88%)</title><rect x="128.9" y="101" width="10.3" height="15.0" fill="rgb(216,98,44)" rx="2" ry="2" />
<text text-anchor="" x="131.90" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>new_heap (1 samples, 0.11%)</title><rect x="1188.7" y="117" width="1.3" height="15.0" fill="rgb(234,172,23)" rx="2" ry="2" />
<text text-anchor="" x="1191.71" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>regex::compile::SuffixCache::get (1 samples, 0.11%)</title><rect x="126.3" y="117" width="1.3" height="15.0" fill="rgb(245,3,29)" rx="2" ry="2" />
<text text-anchor="" x="129.32" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__GI___open64_nocancel (2 samples, 0.22%)</title><rect x="94.0" y="85" width="2.6" height="15.0" fill="rgb(229,78,34)" rx="2" ry="2" />
<text text-anchor="" x="97.01" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_int_malloc (3 samples, 0.33%)</title><rect x="97.9" y="117" width="3.9" height="15.0" fill="rgb(208,115,9)" rx="2" ry="2" />
<text text-anchor="" x="100.89" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__GI___sigprocmask (1 samples, 0.11%)</title><rect x="83.7" y="101" width="1.3" height="15.0" fill="rgb(253,224,8)" rx="2" ry="2" />
<text text-anchor="" x="86.67" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_dl_map_object (2 samples, 0.22%)</title><rect x="171.6" y="117" width="2.5" height="15.0" fill="rgb(218,74,48)" rx="2" ry="2" />
<text text-anchor="" x="174.56" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_int_free (1 samples, 0.11%)</title><rect x="96.6" y="117" width="1.3" height="15.0" fill="rgb(211,141,3)" rx="2" ry="2" />
<text text-anchor="" x="99.59" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_start (8 samples, 0.88%)</title><rect x="149.6" y="117" width="10.3" height="15.0" fill="rgb(238,141,49)" rx="2" ry="2" />
<text text-anchor="" x="152.58" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::num::&lt;impl u64&gt;::overflowing_add (151 samples, 16.54%)</title><rect x="563.2" y="101" width="195.1" height="15.0" fill="rgb(221,14,26)" rx="2" ry="2" />
<text text-anchor="" x="566.17" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >core::num::&lt;impl u64&gt;::ov..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>&lt;regex_syntax::hir::translate::TranslatorI as regex_syntax::ast::visitor::Visitor&gt;::visit_post (1 samples, 0.11%)</title><rect x="55.2" y="85" width="1.3" height="15.0" fill="rgb(229,215,18)" rx="2" ry="2" />
<text text-anchor="" x="58.24" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[unknown] (3 samples, 0.33%)</title><rect x="12.6" y="85" width="3.9" height="15.0" fill="rgb(215,74,30)" rx="2" ry="2" />
<text text-anchor="" x="15.58" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>&lt;I as core::iter::traits::collect::IntoIterator&gt;::into_iter (1 samples, 0.11%)</title><rect x="187.1" y="101" width="1.3" height="15.0" fill="rgb(227,12,21)" rx="2" ry="2" />
<text text-anchor="" x="190.06" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>mmap64 (1 samples, 0.11%)</title><rect x="161.2" y="117" width="1.3" height="15.0" fill="rgb(211,48,5)" rx="2" ry="2" />
<text text-anchor="" x="164.22" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>open_path (1 samples, 0.11%)</title><rect x="172.8" y="101" width="1.3" height="15.0" fill="rgb(222,78,10)" rx="2" ry="2" />
<text text-anchor="" x="175.85" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>mmap64 (2 samples, 0.22%)</title><rect x="119.9" y="117" width="2.5" height="15.0" fill="rgb(216,167,8)" rx="2" ry="2" />
<text text-anchor="" x="122.86" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>clap::args::arg::Arg::long (1 samples, 0.11%)</title><rect x="50.1" y="101" width="1.3" height="15.0" fill="rgb(213,1,45)" rx="2" ry="2" />
<text text-anchor="" x="53.07" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::iter::range::&lt;impl core::iter::traits::iterator::Iterator for core::ops::range::Range&lt;A&gt;&gt;::next (63 samples, 6.90%)</title><rect x="349.9" y="101" width="81.4" height="15.0" fill="rgb(245,200,3)" rx="2" ry="2" />
<text text-anchor="" x="352.91" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >core::ite..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__getrlimit (1 samples, 0.11%)</title><rect x="163.8" y="85" width="1.3" height="15.0" fill="rgb(252,1,48)" rx="2" ry="2" />
<text text-anchor="" x="166.80" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>std::sync::mutex::Mutex&lt;T&gt;::new (1 samples, 0.11%)</title><rect x="127.6" y="117" width="1.3" height="15.0" fill="rgb(222,117,29)" rx="2" ry="2" />
<text text-anchor="" x="130.61" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>dl_main (1 samples, 0.11%)</title><rect x="143.1" y="85" width="1.3" height="15.0" fill="rgb(234,27,18)" rx="2" ry="2" />
<text text-anchor="" x="146.12" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__spawni_child (1 samples, 0.11%)</title><rect x="85.0" y="101" width="1.3" height="15.0" fill="rgb(225,99,53)" rx="2" ry="2" />
<text text-anchor="" x="87.96" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>clap::app::parser::Parser::add_arg (1 samples, 0.11%)</title><rect x="32.0" y="85" width="1.3" height="15.0" fill="rgb(239,212,39)" rx="2" ry="2" />
<text text-anchor="" x="34.97" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>dl_main (1 samples, 0.11%)</title><rect x="167.7" y="85" width="1.3" height="15.0" fill="rgb(236,62,9)" rx="2" ry="2" />
<text text-anchor="" x="170.68" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_start (8 samples, 0.88%)</title><rect x="174.1" y="117" width="10.4" height="15.0" fill="rgb(240,69,0)" rx="2" ry="2" />
<text text-anchor="" x="177.14" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[unknown] (6 samples, 0.66%)</title><rect x="163.8" y="117" width="7.8" height="15.0" fill="rgb(249,158,44)" rx="2" ry="2" />
<text text-anchor="" x="166.80" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__memmove_sse2_unaligned_erms (2 samples, 0.22%)</title><rect x="33.3" y="101" width="2.5" height="15.0" fill="rgb(241,184,27)" rx="2" ry="2" />
<text text-anchor="" x="36.26" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_dl_relocate_object (4 samples, 0.44%)</title><rect x="39.7" y="69" width="5.2" height="15.0" fill="rgb(239,69,40)" rx="2" ry="2" />
<text text-anchor="" x="42.73" y="79.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>do_lookup_x (2 samples, 0.22%)</title><rect x="114.7" y="117" width="2.6" height="15.0" fill="rgb(208,198,16)" rx="2" ry="2" />
<text text-anchor="" x="117.69" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__pthread_once_slow (1 samples, 0.11%)</title><rect x="37.1" y="101" width="1.3" height="15.0" fill="rgb(244,172,31)" rx="2" ry="2" />
<text text-anchor="" x="40.14" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_dl_check_map_versions (1 samples, 0.11%)</title><rect x="140.5" y="101" width="1.3" height="15.0" fill="rgb(228,184,34)" rx="2" ry="2" />
<text text-anchor="" x="143.54" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>&lt;std::collections::hash::map::HashMap&lt;K,V,S&gt; as core::iter::traits::collect::FromIterator&lt; (1 samples, 0.11%)</title><rect x="11.3" y="117" width="1.3" height="15.0" fill="rgb(212,39,4)" rx="2" ry="2" />
<text text-anchor="" x="14.29" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__close (1 samples, 0.11%)</title><rect x="30.7" y="85" width="1.3" height="15.0" fill="rgb(222,76,38)" rx="2" ry="2" />
<text text-anchor="" x="33.68" y="95.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__open64 (1 samples, 0.11%)</title><rect x="35.8" y="101" width="1.3" height="15.0" fill="rgb(244,93,17)" rx="2" ry="2" />
<text text-anchor="" x="38.85" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[unknown] (1 samples, 0.11%)</title><rect x="163.8" y="101" width="1.3" height="15.0" fill="rgb(239,51,23)" rx="2" ry="2" />
<text text-anchor="" x="166.80" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__read_nocancel (1 samples, 0.11%)</title><rect x="38.4" y="101" width="1.3" height="15.0" fill="rgb(211,28,5)" rx="2" ry="2" />
<text text-anchor="" x="41.43" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::num::&lt;impl u64&gt;::checked_add (76 samples, 8.32%)</title><rect x="464.9" y="101" width="98.3" height="15.0" fill="rgb(235,223,40)" rx="2" ry="2" />
<text text-anchor="" x="467.94" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >core::num::..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>prime_factors::is_prime (174 samples, 19.06%)</title><rect x="963.8" y="101" width="224.9" height="15.0" fill="rgb(253,9,33)" rx="2" ry="2" />
<text text-anchor="" x="966.82" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >prime_factors::is_prime</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::ptr::swap_nonoverlapping_one (44 samples, 4.82%)</title><rect x="890.2" y="101" width="56.8" height="15.0" fill="rgb(213,166,43)" rx="2" ry="2" />
<text text-anchor="" x="893.15" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >core::..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_xstat (1 samples, 0.11%)</title><rect x="148.3" y="101" width="1.3" height="15.0" fill="rgb(240,186,25)" rx="2" ry="2" />
<text text-anchor="" x="151.29" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>regex::re_unicode::Regex::new (1 samples, 0.11%)</title><rect x="55.2" y="101" width="1.3" height="15.0" fill="rgb(229,130,22)" rx="2" ry="2" />
<text text-anchor="" x="58.24" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[unknown] (31 samples, 3.40%)</title><rect x="16.5" y="117" width="40.0" height="15.0" fill="rgb(233,28,22)" rx="2" ry="2" />
<text text-anchor="" x="19.46" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >[un..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[unknown] (13 samples, 1.42%)</title><rect x="128.9" y="117" width="16.8" height="15.0" fill="rgb(240,44,43)" rx="2" ry="2" />
<text text-anchor="" x="131.90" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>hashbrown::raw::RawTable&lt;T&gt;::reserve_rehash (1 samples, 0.11%)</title><rect x="51.4" y="101" width="1.3" height="15.0" fill="rgb(240,142,23)" rx="2" ry="2" />
<text text-anchor="" x="54.36" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_int_free (1 samples, 0.11%)</title><rect x="47.5" y="101" width="1.3" height="15.0" fill="rgb(221,144,9)" rx="2" ry="2" />
<text text-anchor="" x="50.48" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_dl_sysdep_start (2 samples, 0.22%)</title><rect x="166.4" y="101" width="2.6" height="15.0" fill="rgb(209,159,31)" rx="2" ry="2" />
<text text-anchor="" x="169.39" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__memmove_sse2_unaligned_erms (1 samples, 0.11%)</title><rect x="86.3" y="117" width="1.2" height="15.0" fill="rgb(230,127,52)" rx="2" ry="2" />
<text text-anchor="" x="89.25" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>prime_factors-0 (27 samples, 2.96%)</title><rect x="128.9" y="133" width="34.9" height="15.0" fill="rgb(214,152,28)" rx="2" ry="2" />
<text text-anchor="" x="131.90" y="143.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  >pr..</text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>pthread_cond_timedwait@@GLIBC_2.3.2 (1 samples, 0.11%)</title><rect x="144.4" y="101" width="1.3" height="15.0" fill="rgb(219,196,41)" rx="2" ry="2" />
<text text-anchor="" x="147.41" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>cfree@GLIBC_2.2.5 (1 samples, 0.11%)</title><rect x="48.8" y="101" width="1.3" height="15.0" fill="rgb(211,98,36)" rx="2" ry="2" />
<text text-anchor="" x="51.77" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_start (10 samples, 1.10%)</title><rect x="101.8" y="117" width="12.9" height="15.0" fill="rgb(209,80,53)" rx="2" ry="2" />
<text text-anchor="" x="104.76" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__xstat64 (3 samples, 0.33%)</title><rect x="88.8" y="117" width="3.9" height="15.0" fill="rgb(240,175,53)" rx="2" ry="2" />
<text text-anchor="" x="91.84" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>__close (1 samples, 0.11%)</title><rect x="20.3" y="37" width="1.3" height="15.0" fill="rgb(234,186,14)" rx="2" ry="2" />
<text text-anchor="" x="23.34" y="47.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>[cargo] (3 samples, 0.33%)</title><rect x="12.6" y="117" width="3.9" height="15.0" fill="rgb(244,24,24)" rx="2" ry="2" />
<text text-anchor="" x="15.58" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>&lt;&amp;T as core::fmt::Display&gt;::fmt (1 samples, 0.11%)</title><rect x="10.0" y="117" width="1.3" height="15.0" fill="rgb(217,157,54)" rx="2" ry="2" />
<text text-anchor="" x="13.00" y="127.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>OPENSSL_LH_insert (2 samples, 0.22%)</title><rect x="12.6" y="69" width="2.6" height="15.0" fill="rgb(248,213,53)" rx="2" ry="2" />
<text text-anchor="" x="15.58" y="79.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>core::mem::size_of (13 samples, 1.42%)</title><rect x="431.3" y="101" width="16.8" height="15.0" fill="rgb(251,104,4)" rx="2" ry="2" />
<text text-anchor="" x="434.34" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>_dl_cache_libcmp (1 samples, 0.11%)</title><rect x="147.0" y="101" width="1.3" height="15.0" fill="rgb(228,190,18)" rx="2" ry="2" />
<text text-anchor="" x="150.00" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
<g class="func_g" onmouseover="s(this)" onmouseout="c()" onclick="zoom(this)">
<title>&lt;std::path::Components as core::iter::traits::iterator::Iterator&gt;::next (1 samples, 0.11%)</title><rect x="16.5" y="101" width="1.3" height="15.0" fill="rgb(214,52,27)" rx="2" ry="2" />
<text text-anchor="" x="19.46" y="111.5" font-size="12" font-family="Verdana" fill="rgb(0,0,0)"  ></text>
</g>
</svg>
