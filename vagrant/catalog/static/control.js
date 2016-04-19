$( document ).ready(function(){
  $('#background_layer').height($('#first_layer').height());
  $('#background_layer').show("fast");
  $("#first_layer p")
          .hide()
          .first()
          .show("fast", function showNext(){
            $(this).next('p').show("fast", showNext);
          })
          .delay(1000)
          .last()
          .hide("slow", function hideNext(){
            if ($(this).next('p').length == 0){
              $('#background_layer').hide("slow");
              $("#first_layer p").remove();
            }
            $(this).next('p').hide("slow", hideNext);
          });
  /* gapi.load('auth2', function() {
    gapi.auth2.init();
  }); */
});

function onLoad() {
  if (gapi.auth2 == undefined) {
    gapi.load('auth2', function() {
      gapi.auth2.init();
    });
    //attachSignin($('#customBtn'));
  }
}

$('form.login #email').on('input', validate_email)

function validate_email(){
  input_email = $(this).val();
  email_format = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
  if (input_email == ''){
    $("form.login .error").html('');
  }else if (input_email.match(email_format) == null){
    console.log(input_email.match(email_format))
    $("form.login .error").html('This e-mail address is invalid.');
  }else{
    $("form.login .error").html('Okay!');
  }
}

/*
  $(".logind .subcomp").hide().first().show("fast", function showNext(){
    $(this).next('div').show("fast", showNext);
  });

$(".login_required").mouseenter(function (event){
  $(".login .subcomp").stop()
  $(".login .subcomp").first().show("fast", function showNext(){
    $(this).next('div').show("fast", showNext);
  });
});
$(".login_required").mouseleave(function (event){
  $(".login .subcomp").stop()
  $(".login .subcomp").first().hide("fast", function showNext(){
    $(this).next('div').hide("fast", showNext);
  });
});
*/

function onSignIn(googleUser) {
  $("form.login .error").html('Verifying google signin...');
  var profile = googleUser.getBasicProfile();
  console.log('ID: ' + profile.getId()); // Do not send to your backend! Use an ID token instead.
  console.log('Name: ' + profile.getName());
  console.log('Image URL: ' + profile.getImageUrl());
  console.log('Email: ' + profile.getEmail());
  // window.location.href = "{{ redirect_in_template(url_for('category.home')) }}"
  
  // send token to the server
  $("form.login .error").html('Sending google token...');
  var id_token = googleUser.getAuthResponse().id_token;
  var xhr = new XMLHttpRequest();
  url = 'http://localhost:5000/googlesignin';
  if ($('._csrf_token').val()){
    param = '?_csrf_token=' + $("._csrf_token").val();
    url = url + param
  }
  xhr.open('POST', url, true);
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
    console.log('Signed in as: ' + xhr.responseText);
    console.log('Token is: ' + id_token);
    console.log('redirect...');
    window.location.href = redirect_url_for_home();
  };
  xhr.send('idtoken=' + id_token);
}

function signOut() {
  console.log(gapi)
  var auth2 = gapi.auth2.getAuthInstance();
  auth2.signOut().then(function () {
    console.log('User signed out.');
    window.location.href = url_for_logout();
  });
}

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#image-preview').attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}

$("#item-upload_image").change(function () {
        readURL(this);
    });