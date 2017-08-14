// counter to give unique id to uploaded images
var imgNo = 0;
// will contain length of video in HH:MM:SS format
var videoLength;
// boolean to control if form can be submitted
var FormCanSubmit = false;

$(document).ready(function(){

    var csrftoken = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
    });

    // start video upload and show rest of form when file is selected
    $("#file").change(function (){
        var form_data = new FormData($('#file_upload')[0]);
        //start video upload
        $.ajax({
            type: 'POST',
            url: '/upload',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            // this part is progress bar
            xhr: function () {
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function (evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = evt.loaded / evt.total;
                        percentComplete = parseInt(percentComplete * 100);
                        $('.myprogress').text(percentComplete + '%').css('width', percentComplete + '%');
                    }
                }, false);
                return xhr;
            },
            success: function(data) {
                console.log("FILE UPLOAD: successful upload");
                var JSONdata = JSON.parse(data);
                // assign video id to the video_details form
                $('#video_id').val(JSONdata.video_id);

                // set the video duration limit
                videoLength = convert_second_to_timestamp(JSONdata.streams[0].duration);

                // set crop values
                $('#crop_start').val("00:00:00");
                $('#crop_end').val(videoLength);

                // show video details
                $("#video_err").hide();
                $("#video_filename").find('span').text(JSONdata.format.filename);

                var videoWidth, videoHeight;

                // find video stream and get size
                JSONdata.streams.forEach(function(stream){
                    if(stream.codec_type == "video"){
                        videoWidth = stream.width;
                        videoHeight = stream.height;
                    }
                });

                $("#video_resolution").find("span")
                    .text(videoWidth + "x" + videoHeight);
            },
            error: function(data, textStatus, errorThrown) {
                console.log("FILE UPLOAD: unsuccessful upload");
                var err = JSON.parse(data.responseText).err;
                $("#video_err").show().text(err);
                reset_form();
            },
            complete: function(){
                // hide spinner loaders
                $(".loader").hide();
            }
        });

        // show the rest of the form
        $("#video_details").show();

        // show the spinners
        $(".loader").css("display", "inline-block");
    });

    // show crop options if crop checkbox is selected
    $("#crop_bool").change(function() {
        if(this.checked) {
            $("#crop_times").show();
        } else {
            $("#crop_times").hide();
        }
    });

    // add an image upload form when add image btn is clicked
    $("#add_image_btn").click(function(e){
        e.preventDefault();
        if(imgNo > 0) {
            console.log('adding form');
            // build image upload form
            var $img = $("<div>", {class: "image_form", id: "img" + imgNo, style: "display: block"});
            $('<h3>').text("Add an image").appendTo($img);
            $('<input>').attr({
                type: 'file',
                id: 'images-' + imgNo + '-img_upload',
                name: 'images-' + imgNo + '-img_upload',
                class: 'img_upload'
            }).appendTo($img);

            $("<label>").attr({"for": 'images-' + imgNo + '-img_upload',
                class: "img_upload_label"}).text("Choose a file").appendTo($img);

            $("<p>").attr({class: "img_filename"}).appendTo($img);
            $img.append("<br>");
            $('<label>').text("Duration (format HH:MM:SS)").appendTo($img);
            $img.append("<br>");

            $('<input>').attr({
                type: 'text',
                id: 'images-' + imgNo + '-duration',
                name: 'images-' + imgNo + '-duration',
                class: 'img_upload_stop'
            }).appendTo($img);
            $img.append("<br>");
            $('<label>').text("Slide type").appendTo($img);
            var $type_radio = $('<ul>', {class: "type_radio", id: 'images-' + imgNo + '-slide_type'});
            var $li = $("<li>")
            $("<input>", {
                id: "images-"+imgNo+"-slide_type-0",
                name: "images-"+imgNo+"-slide_type",
                type: "radio",
                value: "intro"
            }).attr('checked', 'checked').appendTo($li);
            $("<label>", {for: "images-"+imgNo+"-slide_type-0"}).text("Intro slide").appendTo($li);
            $li.appendTo($type_radio);

            var $li2 = $("<li>")
            $("<input>", {
                id: "images-"+imgNo+"-slide_type-1",
                name: "images-"+imgNo+"-slide_type",
                type: "radio",
                value: "outro"
            }).appendTo($li2);
            $("<label>", {for: "images-"+imgNo+"-slide_type-1"}).text('Outro slide').appendTo($li2);
            $li2.appendTo($type_radio);
            $type_radio.appendTo($img);
            $('<button/>', {text: "X", class: "remove_img"}).appendTo($img);
            $("#added_images").prepend($img);
            imgNo++;
        } else {
            console.log("First form show");
            $(".image_form").show();
            imgNo++;
        }
    });

    // when file is selected show filename to user
    $(document).on('change', '.img_upload', function() {
        console.log("File selected");
        var fullPath = $(this).val();
        var filename = getFileName(fullPath);
        // assign filename to label
        if(filename){
            $(this).siblings(".img_filename").text(filename);
        }
    });

    // remove an image
    $(document).on('click', '.remove_img', function(event) {
        event.preventDefault();
        var $elements = $('.image_form');
        var revIndex = $(this).parent().index(".image_form");
        var index = ($elements.length - revIndex ) - 1;
        console.log(index + " " + $elements.length);

        if(imgNo > 1) {
            console.log("removing image");
            $(this).closest(".image_form").remove();
        } else {
            $(".image_form").hide();
        }
        imgNo--;
        // re-assign ids to images
        reformatIds($elements);
    });

    // Validate form, returning on failure.
    $("#video_details_form").on("submit", function(event) {
        event.preventDefault();
        var validated = true;

        // check crop times if checkbox is selected
        if($('#crop_bool').is(':checked')){
            var time = $('#crop_start').val();
            console.log(time_is_within_limits(time, videoLength));
            if(!checkTime(time) || !time_is_within_limits(time, videoLength)) {
                console.log("Start time in wrong format!");
                validated = false
            }

            time = $('#crop_end').val();
            if(!checkTime(time) || !time_is_within_limits(time, videoLength)) {
                console.log("Stop time in wrong format!");
                validated = false
            }
        }

        if(validated) {

            var formData = new FormData(this);
            $.ajax({
                url: '/',
                type: 'POST',
                data: formData,
                cache: false,
                contentType: false,
                processData: false
            });
            $("#tool").hide();
            $("#job_submitted").show();

        } else {
            console.log('not valodiated');
        }
    });

    // warn user if the time format is wrong in real time
    $(document).on('change', "#crop_start, #crop_end, .img_upload_start", function(){
        if(!checkTime($(this).val())) {
            console.log("Wrong time format");
            $(this).next('.warning').remove();
            var $warning = "<div class='warning'>" +
                "<h3>Wrong time Format!</h3>" +
                "</div>";
            $(this).after($warning);
            return;
        } if(!time_is_within_limits($(this).val(), videoLength)){
             $(this).next('.warning').remove();
            var $warning =      "<div class='warning'>" +
                                    "<h3>Time is longer than video time ( "+ videoLength +" )</h3>" +
                                "</div>";
            $(this).after($warning);
        } else{
            console.log("Correct time format!");
            $(this).next(".warning").hide();
        }
    });

    $(document).on('change', '#crop_start', function(){
        if($(this).val() >= $('#crop_end').val()){
            console.log("TIME ERR: start time has to be smaller than stop time");
            $(this).next('.warning').remove();
            var $warning = "<div class='warning'>" +
                "<h3>Start time has to be smaller than stop time</h3>" +
                "</div>";
            $(this).after($warning);
        }
    });



}); // end jquery

// extract the file name from the full path of uploaded video
var getFileName = function(fullPath){
    if (fullPath) {
        var startIndex = (fullPath.indexOf('\\') >= 0 ? fullPath.lastIndexOf('\\') : fullPath.lastIndexOf('/'));
        var filename = fullPath.substring(startIndex);
        if (filename.indexOf('\\') === 0 || filename.indexOf('/') === 0) {
            filename = filename.substring(1);
        }
        return filename;
    }
    return null;
};

// regex to match HH.MM.SS
var checkTime = function(time){
    var re = new RegExp('([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]');
    return re.test(time)
};

// when an image is deleted, reformat the ids from 0 to imgNo (important for flask-wtf)
var reformatIds = function(images){

    for( var i = 0 ; i <= imgNo - 1; i++){
        var index =imgNo - i - 1;
        var $img = images.eq(i);
        $img.attr('id', "img" + index);
        $img.find('.img_upload').attr("id", "images-" + index + "-img_upload");
        $img.find('.img_upload_label').attr("for", "images-" + index + "-img_upload");
        $img.find('.img_upload_start').attr("id", "images-" + index + "-pic_start");
        $img.find('.img_upload_stop').attr("id", "images-" + index + "-pic_stop");
    }
};

var convert_second_to_timestamp = function(seconds){
    d = parseInt(seconds);
    var h = Math.floor(d / 3600);
    var m = Math.floor(d % 3600 / 60);
    var s = Math.floor(d % 3600 % 60);

    return ('0' + h).slice(-2) + ":" + ('0' + m).slice(-2) + ":" + ('0' + s).slice(-2);
};

var time_is_within_limits = function(time1, time2){
    return time1 <= time2;
};

var secondsToHms = function(d) {
    d = Number(d);

    var h = Math.floor(d / 3600);
    var m = Math.floor(d % 3600 / 60);
    var s = Math.floor(d % 3600 % 60);

    return ('0' + h).slice(-2) + ":" + ('0' + m).slice(-2) + ":" + ('0' + s).slice(-2);
};

var reset_form = function(){
    $("#video_resolution").find('span').text("");
    $("#video_filename").find('span').text("");
    $("#crop_start, #crop_end").val("");
};