/**
    ModelId
	EnModelUnknown,		//(0)
	EnModelAVRX10,		//(1)
	EnModelAVRX20,		//(2)
	EnModelAVRX30,		//(3)
	EnModelAVRX40,		//(4)
	EnModelAVRX50,		//(5)
	EnModelAVRX70,		//(6)
	EnModelNR15,		//(7)
	EnModelNR16,		//(8)
	EnModelSR50,		//(9)
	EnModelSR60,		//(10)
	EnModelSR70,		//(11)
	EnModelAV77,		//(12)
	EnModelAV88,		//(13)
**/
var _bDebug = location.hostname.indexOf("localhost") != -1;
var g_xmlData = "";

/**
 * String�N���X��trim���\�b�h���ǉ�
 */
String.prototype.trim = function() {
	return this.replace(/^\s+|\s+$/g, '');
}

/**
 * �A�v���P�[�V�����J�n�B
 *
 * @since	2008/12/26
 * @version	0.0.1
 */
function appStart() {
	var fill = $("#fill");
	// �S�Ă̒ʐM�ɑ΂��ăC�x���g���X�i�o�^�B�ʐM���̓y�[�W�S�̂Ƀt�B���^���|�����B
		$().ajaxSend(function(event, XMLHttpRequest, options) {
		if (isNaN(options.bFill) || options.bFill) {
			$("#fill").focus().css("display", "block");
		}
	}).ajaxComplete(function(event, XMLHttpRequest, options) {
		if (options.url.indexOf(".xml") < 0) {
			fill.css("display", "none");
		}
	}).ajaxError(function() {
		fill.css("display", "none");
	});
	// #fill �̒�����������
	$.get("/_fill.html", null, function(data, status) {
		fill.html(data);
	});
	// �A�v���P�[�V����������
		initApp();
	// asp�������p�ʐM
	var url;
	if (_bDebug) {
//		url = "./index.html.init.asp";
//		url = "../proxy.php?url=" + encodeURI("MainZone/index.html.init.asp");
	} else {
		url = "./index.html.init.asp";
	}
	$.get(url, null, function(data, status) {
		// �������Ԏ擾�J�n�B
		loadMainXml(true);

		// �����X�V�B
		setInterval(function(){
			loadMainXml(false);
		}, 1000);

	}, "text");

	//���ʕ`�掞��Cookie��������
//	$("div.menuItem a").click(function(event) {
		$.cookie("ZoneName", $("title").html(), {
			expires: 365,
			path: '/'
		});
//		return true;
//	});
}

/**
 * �y�[�W�\���pxml�̓ǂݍ���
 *
 * @param {bool} bFill	�ʐM��"connecting"�\�������Ȃ���true�B�����ĕ`�悩�����ĕ`�悩�Ő؂��ς����B
 */
function loadMainXml(bFill) {
	var url = "";
	if (_bDebug) {
//		url = "/proxy.php?url=" + encodeURI("goform/formMainZone_MainZoneXml.xml");
		url = "/goform/formMainZone_MainZoneXml.xml";
	} else {
		url = "/goform/formMainZone_MainZoneXml.xml";
	}
	// �ʐM���ɗ��ǂ݂̃����[�h�v���͒e���B
	if( !bFill && this.ajax ) {
		return;
	}
	this.ajax = $.ajax({
		url: url, // �ڑ���URL
		bFill: bFill,
		cache: false, // �L���b�V�����Ȃ�
		success: function(data) { // �ʐM�������̃R�[���o�b�N�֐�
			parent.ajax = null;
			data = $(data);
			if ( !bFill && g_xmlData && g_xmlData.text() == data.text()) {
				$("#fill").css("display", "none");
				return;
			}
			data.getValue = function(param) {
				var ret = this.find(param + " value");
				if (ret.length == 1) {
					return ret.text();
				} else {
					return ret;
				}
			}
			data.getVolume = function(vol) {
				if (vol == undefined) {
					vol = this.getValue("MasterVolume");
				}
				if (this.isAbsolute() ) {
					if (vol == "--") {
//						vol = -81.0;
						vol = -80.0;
					}
//					return (parseFloat(vol) + 81.0).toFixed(1).toString();
					return (parseFloat(vol) + 80.0).toFixed(1).toString();
				} else {
					return vol + " dB";
				}
			}
			data.isAbsolute = function() {
				return this.getValue("VolumeDisplay") == "Absolute";
			}
			g_xmlData = data;
			parsePowerXml(data);
			parseFuncXml(data);
			parseSurroundXml(data);
			parseVolumeXml(data);
			$("#fill").css("display", "none");
		},
		error: function(XMLHttpRequest) { // �ʐM�G���[�������̃R�[���o�b�N�֐�
			parent.ajax = null;
			if ( bFill ) {
				alert("connection failed\n");
			}
		}
	});
}

/**
 * �A�v���P�[�V�����̏������B�C�x���g���X�i�̓o�^�ȂǁB
 *
 * @since	2008/12/26
 * @version	0.0.1
 */
function initApp() {
	// �����[�h�{�^���̃C�x���g�n���h���o�^
	$("div#Reload a").click(function(event) {
		location.reload();
		return false;
	});
// �����N�N���b�N����cookie��zone�������������ł����B�Ƃ肠����365���ԗL���B
//	$("div.menuItem a").click(function(event) {
//		$.cookie("ZoneName", $("title").html(), {
//			expires: 365,
//			path: '/'
//		});
//		return true;
//	});

	// Sleep
	$( "div#SleepTimer select" ).change(function(event){
		putRequest({
			cmd0: "PutSleepTimer/" + event.target.value,
			cmd1: "aspMainZone_WebUpdateStatus/"
		}, true, true);
		return false;
		event.target.selectedIndex = 0;
	});
	
	// Video Select
	$( "div#VideoSelect select" ).change(function(event){
		putRequest({
			cmd0: "PutVideoSelect/" + event.target.value,
			cmd1: "aspMainZone_WebUpdateStatus/"
		}, true, true);
		return false;
		event.target.selectedIndex = 0;
	});

	// ECO Mode
	$( "div#ECOMode select" ).change(function(event){
		putRequest({
			cmd0: "PutECOMode/" + event.target.value,
			cmd1: "aspMainZone_WebUpdateStatus/"
		}, true, true);
		return false;
		event.target.selectedIndex = 0;
	});


	// Add Source
	$( "div#AddSource div.AddSourceLabel select" ).change(function(event){
		putRequest({
			cmd0: "PutZone_InputFunction/" + event.target.value,
			cmd1: "aspMainZone_WebUpdateStatus/"
		}, true, true);
		return false;
		event.target.selectedIndex = 0;
	});

//Quick Select
	appendQSSelect($("div#QuickSelect div.btnQSS1"), "1", "1");
	appendQSSelect($("div#QuickSelect div.btnQSS2"), "2", "2");
	appendQSSelect($("div#QuickSelect div.btnQSS3"), "3", "3");
	appendQSSelect($("div#QuickSelect div.btnQSS4"), "4", "4");

//Surround
	appendSoundMode($("div#Surround div.btnMOVIE"), "MOVIE", "MOVIE");
	appendSoundMode($("div#Surround div.btnMUSIC"), "MUSIC", "MUSIC");
	appendSoundMode($("div#Surround div.btnGAME"), "GAME", "GAME");
	appendSoundMode($("div#Surround div.btnPURE"), "PURE", "PURE DIRECT");

//Volume
	appendMute($("div#Volume div.btnVolMute"), "Mute", "TOGGLE");
	appendVolume($("div#Volume div.btnVolUp"), "+", ">");
	appendVolume($("div#Volume div.btnVolDown"), "-", "<");
}

/**
 * �}�E�X�I�[�o�[�ŉ摜�����ւ�����a�^�O�𐶐������B
 *
 * @since 2009/1/14
 * @param {int} x	x�T�C�Y�B30/60/90/180�̉��ꂩ
 * @param {String} link	�����N���B�Ƃ肠����"#"��OK�B
 * @param {String} str	�{�^���ɋL�q���镶�����B
 */
function createButton(x, link, str) {
	var a = $("<a/>").attr("href", link).addClass("button" + x + "x30");
	a.append($("<span/>").addClass("btnChild").html(str));
	return a;
}

/**
 * �I�����Ԃ̃{�^���摜���쐬�����B
 *
 * @since 2009/1/14
 * @param {int} x	x�T�C�Y�B30/60/90/180�̉��ꂩ
 * @param {String} str	�{�^���ɋL�q���镶�����B
 */
function acreateButtonSelect(x, str) {
	var div = $("<div/>").addClass("button" + x + "x30On");
	div.append($("<span/>").addClass("btnChild").html(str));
	return div;
}


/**
 * �}�E�X�I�[�o�[�ŉ摜�������ւ���input�^�O�𐶐������B
 *
 * @param {String} srcOver
 * @param {String} srcOn
 */
function createSwapInput(srcOn, srcOver) {
	var imgOn = $("<img/>").attr("src", srcOn).css("display", "none");
	var imgOver = $("<img/>").attr("src", srcOver).css("display", "none");
	var input = $("<input type=\"image\" />").attr("src", srcOn).attr("alt", name);
	// �}�E�X�I�[�o�[�ŉ摜�����ւ�
	input.hover(function() {
		input.attr("src", imgOver.attr("src"));
	}, function() {
		input.attr("src", imgOn.attr("src"));
	});
	// �u���E�U�ɃL���b�V�������邽�߁Abody�ɔ��\����img�^�O���ǉ��B
	$().append(imgOn).append(imgOver);
	return input;
}


/**
 * "/goform/formMainZone_MainZoneXml.xml" ���p�[�X����html���\�z�����BPower�����{TopMenu�����N
 *
 * @since	2009/1/7
 * @param {XMLDocument} data ./index.html.xml.asp �̓ǂݍ��݌���
 */
function parsePowerXml(data) {
	//===========

	// TopMenu
	if (data.getValue("TopMenuLink").toUpperCase() == "ON") {
		$("div#TopMenu").css("visibility", "visible");
	} else {
		$("div#TopMenu").css("visibility", "hidden");
	}

	//Friendly Name
	$("h2").html(data.getValue("FriendlyName"));

	//===========
	// ZonePower
	if (data.getValue("ZonePower") == "ON") {
		$("div#powerBtn div.RPowerBtn").empty().append(createSwapInput("../img/Power_On.png", "../img/Power_On_MO.png").click(function() {
			putRequest({
				cmd0: "PutZone_OnOff/OFF",
				cmd1: "aspMainZone_WebUpdateStatus/"
			}, true, true);
			return false;
		}));
	} else {
		$("div#powerBtn div.RPowerBtn").empty().append(createSwapInput("../img/Power_OFF.png", "../img/Power_OFF_MO.png").click(function() {
			putRequest({
				cmd0: "PutZone_OnOff/ON",
				cmd1: "aspMainZone_WebUpdateStatus/"
			}, true, true);
			return false;
		}));
	}

	//===========
	// RenameZone
	$("div.RParamZoneName").html(data.getValue("RenameZone"));


	// Sleep Timer
	var ListTimer = $( "div#SleepTimer select" ).empty();
	var ListOff = data.getValue("SleepOff");

	var opt = $( "<option/>" );
	opt.html( "" ).attr( "value", "" );
	ListTimer.append( opt );

	var opt = $( "<option/>" );
//	opt.html( "OFF" ).attr( "value", "OFF" );
	opt.html( ListOff ).attr( "value", "OFF" );
	ListTimer.append( opt );

	for( var cnt=1; cnt<=12; cnt+=1 ) {
		var opt = $( "<option/>" );
		var timer = cnt*10;
		if(timer<10){
			opt.html( timer ).attr( "value", ("00" + timer) );
		}else if(timer<100){
			opt.html( timer ).attr( "value", ("0" + timer) );
		}else{
			opt.html( timer ).attr( "value", timer );
		}
		ListTimer.append( opt );
	}

/**

	// Video Select
	var VideoSelectSelected = data.find( "VideoSelect value" ).text();
	var VideoSelectOnOff = data.find( "VideoSelectOnOff value" ).text();
	var VideoSelectDisp = data.find( "VideoSelectDisp value" ).text();
	var VideoSelect = $("div#VideoSelect select").empty();
	
	if(VideoSelectDisp=="ON"){
		$("div#VideoSelect").css("visibility", "visible");
	}else{
		$("div#VideoSelect").css("visibility", "hidden");
	}
	
	data.find("VideoSelectLists value").each(function(index){
		var value = $(this);
		var index = value.attr("index");
//		var table = value.attr("table");
//		var param = $.trim(value.attr("param"));
		var table = data.find( "VideoSelectLists value" ).text();

		var opt = $("<option/>");
		opt.html(table).attr( "value", index );;

		if(VideoSelectOnOff=="ON"){
			if( index == VideoSelectSelected ) {
				opt.attr( "selected", true );
			}
		}else{
			if( index == "OFF" ) {
				opt.attr( "selected", true );
			}
		}
		VideoSelect.append(opt);
	});
**/
	// ECO Mode
	var ECOModeSelected = data.find( "ECOMode value" ).text();
	var ECOModeDisp = data.find( "ECOModeDisp value" ).text();
	var ECOMode = $("div#ECOMode select").empty();
	
	if(ECOModeDisp=="ON"){
		$("div#ECOMode").css("display", "block");
		$("div#ECOMode").css("visibility", "visible");
		
		data.find("ECOModeLists value").each(function(index){
			var value = $(this);
			var index = value.attr("index");
			var table = value.attr("table");
			var param = $.trim(value.attr("param"));
			var opt = $("<option/>");
			opt.html(table).attr( "value", index );;
			if(ECOModeSelected=="ON"){
				if( index == "ON" ) {
					opt.attr( "selected", true );
				}
			}else if(ECOModeSelected=="AUTO"){
				if( index == "AUTO" ) {
					opt.attr( "selected", true );
				}
			}else{
				if( index == "OFF" ) {
					opt.attr( "selected", true );
				}
			}
			ECOMode.append(opt);
		});
		
	}else{
		$("div#ECOMode").css("display", "none");
		$("div#ECOMode").css("visibility", "hidden");
	}

}

/**
 * "/goform/formMainZone_MainZoneXml.xml" ���p�[�X����html���\�z�����BSource����
 *
 * @since	2009/1/7
 * @param {XMLDocument} data ./index.html.xml.asp �̓ǂݍ��݌���
 */
function parseFuncXml(data) {
	var selectSource = data.getValue("InputFuncSelect");
	var rename = data.find("RenameSource value");
	var source = data.find("InputFuncList value");

	//Source Area
	if(parseInt( data.getValue( "ModelId" ) ) == 1){ // EnModelAVRX10
		$("div#S3").css("display", "block");
		appendSource($("div#S3 div.btn31"), $("<div>CBL/SAT</div>"), "SAT/CBL");
		appendSource($("div#S3 div.btn32"), $("<div>DVD/Blu-ray</div>"), "DVD");
		appendSource($("div#S3 div.btn33"), $("<div>Blu-ray</div>"), "BD");
		appendSource($("div#S3 div.btn34"), $("<div>Game</div>"), "GAME");
		appendSource($("div#S3 div.btn35"), $("<div>AUX</div>"), "AUX1");
		appendSource($("div#S3 div.btn36"), $("<div>Media Player</div>"), "MPLAY");
		appendSource($("div#S3 div.btn37"), $("<div>iPod/USB</div>"), "USB/IPOD");
		appendSource($("div#S3 div.btn38"), $("<div>TV Audio</div>"), "TV");
		appendSource($("div#S3 div.btn39"), $("<div>Tuner</div>"), "TUNER");
		appendSource($("div#S3 div.btn310"), $("<div>Online Music</div>"), "NETHOME");
		appendSource($("div#S3 div.btn311"), $("<div>Bluetooth</div>"), "BT");
		appendSource($("div#S3 div.btn312"), $("<div>Internet Radio</div>"), "IRP");
		$("div#S3 div.btn313").css("display", "none");
		$("div#S3 div.btn314").css("display", "none");
		$("div#S3 div.btn315").css("display", "none");

	}else if(parseInt( data.getValue( "ModelId" ) ) == 7){ // EnModelNR15
		$("div#S3").css("display", "block");
		appendSource($("div#S3 div.btn31"), $("<div>CBL/SAT</div>"), "SAT/CBL");
		appendSource($("div#S3 div.btn32"), $("<div>Media Player</div>"), "MPLAY");
		appendSource($("div#S3 div.btn33"), $("<div>Blu-ray/DVD</div>"), "BD");
		appendSource($("div#S3 div.btn34"), $("<div>Game</div>"), "GAME");
		appendSource($("div#S3 div.btn35"), $("<div>AUX</div>"), "AUX1");
		appendSource($("div#S3 div.btn36"), $("<div>Tuner</div>"), "TUNER");
		appendSource($("div#S3 div.btn37"), $("<div>iPod/USB</div>"), "USB/IPOD");
		appendSource($("div#S3 div.btn38"), $("<div>TV Audio</div>"), "TV");
		appendSource($("div#S3 div.btn39"), $("<div>CD</div>"), "CD");
		appendSource($("div#S3 div.btn310"), $("<div>Online Music</div>"), "NETHOME");
		appendSource($("div#S3 div.btn311"), $("<div>Bluetooth</div>"), "BT");
		appendSource($("div#S3 div.btn312"), $("<div>Internet Radio</div>"), "IRP");
		$("div#S3 div.btn313").css("display", "none");
		$("div#S3 div.btn314").css("display", "none");
		$("div#S3 div.btn315").css("display", "none");


	}else if ((parseInt( data.getValue( "ModelId" ) ) == 2) || // EnModelAVRX20
	          (parseInt( data.getValue( "ModelId" ) ) == 3) || // EnModelAVRX30
	          (parseInt( data.getValue( "ModelId" ) ) == 8) || // EnModelNR16
	          (parseInt( data.getValue( "ModelId" ) ) == 9)){ // EnModelSR50
		$("div#S3").css("display", "block");
		appendSource($("div#S3 div.btn31"), $("<div>CBL/SAT</div>"), "SAT/CBL");
		appendSource($("div#S3 div.btn32"), $("<div>DVD</div>"), "DVD");
		appendSource($("div#S3 div.btn33"), $("<div>Blu-ray</div>"), "BD");
		appendSource($("div#S3 div.btn34"), $("<div>Game</div>"), "GAME");
		appendSource($("div#S3 div.btn35"), $("<div>AUX1</div>"), "AUX1");
		appendSource($("div#S3 div.btn36"), $("<div>Media Player</div>"), "MPLAY");
		appendSource($("div#S3 div.btn37"), $("<div>TV Audio</div>"), "TV");
		appendSource($("div#S3 div.btn38"), $("<div>AUX2</div>"), "AUX2");
		appendSource($("div#S3 div.btn39"), $("<div>Tuner</div>"), "TUNER");
		appendSource($("div#S3 div.btn310"), $("<div>iPod/USB</div>"), "USB/IPOD");
		appendSource($("div#S3 div.btn311"), $("<div>CD</div>"), "CD");
		appendSource($("div#S3 div.btn312"), $("<div>Bluetooth</div>"), "BT");
		appendSource($("div#S3 div.btn313"), $("<div>Online Music</div>"), "NETHOME");
		appendSource($("div#S3 div.btn314"), $("<div>Media Server</div>"), "SERVER");
		appendSource($("div#S3 div.btn315"), $("<div>Internet Radio</div>"), "IRP");

	}else if(parseInt( data.getValue( "ModelId" ) ) == 10){ // EnModelSR60
		$("div#S3").css("display", "block");
		appendSource($("div#S3 div.btn31"), $("<div>CBL/SAT</div>"), "SAT/CBL");
		appendSource($("div#S3 div.btn32"), $("<div>DVD</div>"), "DVD");
		appendSource($("div#S3 div.btn33"), $("<div>Blu-ray</div>"), "BD");
		appendSource($("div#S3 div.btn34"), $("<div>Game</div>"), "GAME");
		appendSource($("div#S3 div.btn35"), $("<div>AUX1</div>"), "AUX1");
		appendSource($("div#S3 div.btn36"), $("<div>Media Player</div>"), "MPLAY");
		appendSource($("div#S3 div.btn37"), $("<div>TV Audio</div>"), "TV");
		appendSource($("div#S3 div.btn38"), $("<div>AUX2</div>"), "AUX2");
		appendSource($("div#S3 div.btn39"), $("<div>Tuner</div>"), "TUNER");
		appendSource($("div#S3 div.btn310"), $("<div>iPod/USB</div>"), "USB/IPOD");
		appendSource($("div#S3 div.btn311"), $("<div>CD</div>"), "CD");
		appendSource($("div#S3 div.btn312"), $("<div>Bluetooth</div>"), "BT");
		appendSource($("div#S3 div.btn313"), $("<div>Online Music</div>"), "NETHOME");
		appendSource($("div#S3 div.btn314"), $("<div>Phono</div>"), "PHONO");
		appendSource($("div#S3 div.btn315"), $("<div>Internet Radio</div>"), "IRP");

	}else if((parseInt( data.getValue( "ModelId" ) ) == 4) || // EnModelAVRX40
			 (parseInt( data.getValue( "ModelId" ) ) == 5) || // EnModelAVRX50
	         (parseInt( data.getValue( "ModelId" ) ) == 6) || // EnModelAVRX70
	         (parseInt( data.getValue( "ModelId" ) ) == 11) || // EnModelSR70
	         (parseInt( data.getValue( "ModelId" ) ) == 12) || // EnModelAV77
	         (parseInt( data.getValue( "ModelId" ) ) == 13)){ // EnModelAV88
		$("div#S4").css("display", "block");
		appendSource($("div#S4 div.btn41"), $("<div>CBL/SAT</div>"), "SAT/CBL");
		appendSource($("div#S4 div.btn42"), $("<div>DVD</div>"), "DVD");
		appendSource($("div#S4 div.btn43"), $("<div>Media Player</div>"), "MPLAY");
		appendSource($("div#S4 div.btn44"), $("<div>TV Audio</div>"), "TV");
		appendSource($("div#S4 div.btn45"), $("<div>Blu-ray</div>"), "BD");
		appendSource($("div#S4 div.btn46"), $("<div>AUX1</div>"), "AUX1");
		if(parseInt( data.getValue( "ModelId" ) ) == 4){ // EnModelAVRX40
			appendSource($("div#S4 div.btn47"), $("<div>Tuner</div>"), "TUNER");
		}else{
			if(parseInt( data.getValue( "SalesArea" ) ) == 0){ // NA
				appendSource($("div#S4 div.btn47"), $("<div>HD Radio</div>"), "HDRADIO");
			}else{
				appendSource($("div#S4 div.btn47"), $("<div>Tuner</div>"), "TUNER");
			}
		}
		appendSource($("div#S4 div.btn48"), $("<div>Bluetooth</div>"), "BT");
		appendSource($("div#S4 div.btn49"), $("<div>Game</div>"), "GAME");
		appendSource($("div#S4 div.btn410"), $("<div>AUX2</div>"), "AUX2");
		appendSource($("div#S4 div.btn411"), $("<div>Phono</div>"), "PHONO");
		appendSource($("div#S4 div.btn412"), $("<div>iPod/USB</div>"), "USB/IPOD");
		appendSource($("div#S4 div.btn413"), $("<div>CD</div>"), "CD");
		appendSource($("div#S4 div.btn414"), $("<div>Online Music</div>"), "NETHOME");
		appendSource($("div#S4 div.btn415"), $("<div>Media Server</div>"), "SERVER");
		appendSource($("div#S4 div.btn416"), $("<div>Internet Radio</div>"), "IRP");

		if((parseInt( data.getValue( "ModelId" ) ) == 6) || // EnModelAVRX70
	       (parseInt( data.getValue( "ModelId" ) ) == 13)){ // EnModelAV88
	         
			//Additional Source
			if (data.getValue("AddSourceDisplay") == "TRUE") {
				$("div#AddSource").css("display", "block");

				// Additioanl Source
				var ListAddSource = $( "div#AddSource div.AddSourceLabel select" ).empty();

				var opt = $( "<option/>" );
				opt.html( "" ).attr( "value", "" );
				ListAddSource.append( opt );
				
				var opt = $( "<option/>" );
				opt.html( "AUX3" ).attr( "value", "AUX3" );
				ListAddSource.append( opt );
				
				var opt = $( "<option/>" );
				opt.html( "AUX4" ).attr( "value", "AUX4" );
				ListAddSource.append( opt );
				
				var opt = $( "<option/>" );
				opt.html( "AUX5" ).attr( "value", "AUX5" );
				ListAddSource.append( opt );
				
				var opt = $( "<option/>" );
				opt.html( "AUX6" ).attr( "value", "AUX6" );
				ListAddSource.append( opt );
				
				var opt = $( "<option/>" );
				opt.html( "AUX7" ).attr( "value", "AUX7" );
				ListAddSource.append( opt );
			}
		}
	}

		//  Source Name
	$("#source .RParamSource").html(selectSource);

	//  PlayerView
	if(selectSource=="Online Music" || selectSource=="iPod/USB" || selectSource=="Bluetooth" ){
		$("#source .btnPlayerView").html("<a href='../NetAudio/index.html'>PlayerView &gt;</a>");
	}else if(selectSource=="HD Radio"){
		$("#source .btnPlayerView").html("<a href='../Tuner/HDRADIO/index.html'>PlayerView &gt;</a>");
	}else if(selectSource=="Tuner"){
		$("#source .btnPlayerView").html("<a href='../Tuner/TUNER/index.html'>PlayerView &gt;</a>");
	}else{
		$("#source .btnPlayerView").html("&nbsp;");
	}


	if (data.getValue("BrandId") == "DENON_MODEL") {
		$("div#left").css("background-color", "#0e1033");

	   	//LOGO
		$("div#menuItemLogo").html("<img src= ../img/denon_Logo.gif>");

		//Quick Select
		$("#QuickSelectLabel .RParamQuickSelect").html("Quick Select");
		$("div#QuickSelect").css("visibility", "visible");
			}else{
	   $("div#left").css("background-color", "#b3b3b3");

		//LOGO
		$("div#menuItemLogo").html("<img src= ../img/marantz_Logo.png>");

		//Smart Select
		$("#QuickSelectLabel .RParamQuickSelect").html("Smart Select");
		$("div#QuickSelect").css("visibility", "visible");
	}


}


function parseSurroundXml(data) {
	var selectSurround = data.getValue("selectSurround");
	//  Source Name
	$("#SurroundLabel .RParamSoundMode").html(selectSurround);
}

/**
 * "/goform/formMainZone_MainZoneXml.xml" ���p�[�X����html���\�z�����BVolume����
 *
 * @since	2009/1/7
 * @param {XMLDocument} data ./index.html.xml.asp �̓ǂݍ��݌���
 */
function parseVolumeXml(data) {
	var bar;
	var bMute = data.getValue("Mute") != "off";

	//  Source Name
	if (bMute) {
		$("#VolumeLabel .RParamVolume").html("MUTING On");
	} else {
		$("#VolumeLabel .RParamVolume").html(data.getVolume());
	}

}


/**
 *
 * @param {Object} obj		Object
 * @param {String} btn		
 * @param {String} cmd		SI command Option
**/

//function appendSource(obj, btn, cmd) {
function appendSource(obj, labelobj, cmd) {
	obj.empty();
	
	$(obj).empty().append(
		$(labelobj).click(
			function() {
				putRequest({
					cmd0: "PutZone_InputFunction/" + cmd,
					cmd1: "aspMainZone_WebUpdateStatus/"
				}, true, true);
//				setTimeout( function() { JumpPlayView(cmd);}, 1000 );
				setTimeout( function() { JumpPlayView(cmd);}, 3000 );
				
			}));
}

/*
������append�̃h�L�������g�����Ă������A
append()���͂��߁Aprepend()�Ahtml()�Ȃǂ̃��\�b�h�́A�����񂾂��łȂ��AjQuery �I�u�W�F�N�g�����������邱�ƂɋC�Â��B

�Ƃ����킯�ŁA��������$()�ň͂���jQuery�I�u�W�F�N�g���������ɃC�x���g�����Ă��܂��Ηǂ��̂ł����B

$('#seleter').append(
    $('<a href="#">UNKO</a>').click(
        function(){
            //unko
        }
    )
);


*/

function appendQSSelect(obj, btn, cmd) {
	// ���x���ɂ��Ă����ǉ������B
	obj.empty();

	$(obj).empty().click(function(event) {
		putRequest({
			cmd0: "PutUserMode/Quick" + cmd,
			cmd1: "aspMainZone_WebUpdateStatus/"
		}, true, true);
	});
	
	$(obj).empty().append(btn);
	
	return false;

}


function appendSoundMode(obj, btn, cmd) {
	// ���x���ɂ��Ă����ǉ������B
	obj.empty();

	$(obj).empty().click(function(event) {
		putRequest({
			cmd0: "PutSurroundMode/" + cmd,
			cmd1: "aspMainZone_WebUpdateStatus/"
		}, true, true);
	});
	
	$(obj).empty().append(btn);
	
	return false;

}

function appendMute(obj, btn, cmd) {
	// ���x���ɂ��Ă����ǉ������B
	obj.empty();

	$(obj).empty().click(function(event) {
		putRequest({
			cmd0: "PutVolumeMute/" + cmd,
			cmd1: "aspMainZone_WebUpdateStatus/"
		}, true, true);
	});
	
	$(obj).empty().append(btn);
	
	return false;

}


function appendVolume(obj, btn, cmd) {
	// ���x���ɂ��Ă����ǉ������B
	obj.empty();

	$(obj).empty().click(function(event) {
		putRequest({
			cmd0: "PutMasterVolumeBtn/" + cmd,
			cmd1: "aspMainZone_WebUpdateStatus/"
		}, true, true);
	});
	
	$(obj).empty().append(btn);
	

}


/**
 *
 * @param {Object} obj		Object
 * @param {String} imgOn	Normal Image
 * @param {String} imgOver	Mouse Over Image
 * @param {String} cmd		SI command Option
**/

//function appendSourceOld(obj, del, source, rename, values, select, bNet) {
function appendSourceOld(obj, imgOn, imgOver, cmd) {
	// ���x���ɂ��Ă����ǉ������B
	obj.empty();
	
	$(obj).empty().append(createSwapInput(imgOn, imgOver).click(function() {
		putRequest({
			cmd0: "PutZone_InputFunction/" + cmd,
			cmd1: "aspMainZone_WebUpdateStatus/"
		}, true, true);
//		JumpPlayView(cmd);
		setTimeout( function() { JumpPlayView(cmd);}, 1000 );
//		setTimeout( function() { JumpPlayView(cmd);}, 500 );
	}));


}

function JumpPlayView(cmd) {
	
	if(cmd=="TUNER"){
		location.href="/Tuner/TUNER/index.html";
	}else if(cmd=="HDRADIO"){
		location.href="/Tuner/HDRADIO/index.html";
	}else if(cmd=="NETHOME"){
		location.href="/NetAudio/index.html";
	}else if(cmd=="IRP"){
		location.href="/NetAudio/index.html";
	}else if(cmd=="USB/IPOD"){
		location.href="/NetAudio/index.html";
	}else if(cmd=="SERVER"){
		location.href="/NetAudio/index.html";
	}else if(cmd=="BT"){
		location.href="/NetAudio/index.html";
	}
}


/**
 * ./index.put.asp ��data�𑗐M�����B
 *
 * @since	2009/01/09
 * @param {Object} data
 * @param {Object} bReload
 * @param {Object} bFill
 */
function putRequest(data, bReload, bFill) {
	var url = "";
	if (_bDebug) {
		url = "/proxy.php?url=" + encodeURI("MainZone/index.put.asp");
		//url = "/postVar.php";
	} else {
		url = "./index.put.asp";
	}
	$.post(url, data, function(data) {
		if (_bDebug) {
			//alert(data);
		}
		if (bReload) {
			loadMainXml(bFill);
			setTimeout( function() {
				loadMainXml( false );
			}, 2000 );
		}
	});
}

// �v���O�����J�n�B
appStart();
