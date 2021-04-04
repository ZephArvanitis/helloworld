import { removeData } from "jquery";

// toggle enabled/disabled
// Enabled: "bg-indigo-600", Not Enabled: "bg-gray-200"
var enabled_btn_class = "bg-indigo-600";
var disabled_btn_class = "bg-gray-200";
// Enabled: "translate-x-5", Not Enabled: "translate-x-0"
var enabled_span_class = "translate-x-5";
var disabled_span_class = "translate-x-0";

function trialAjaxCall(): Promise<boolean> {
  var url = "/helloworld/random_number";
  var promise = fetch(url, {
      method: "GET",
      headers: {
          "Content-Type": "application/json",
      },
    })
    .then((response) => response.json())
    .then((json) => console.log(json))
    .then(() => true);
  
  return promise;
}

function getUserIds(): number[] {
  var userIds : number[] = [];
  $(".toggle-btn").each(function (x) {
    if (this.classList.contains(enabled_btn_class))
    {
      var elementId = this.id;
      var userId = parseInt(elementId.split('-')[2]);
      userIds.push(userId);
    }
  });
  return userIds;

}

function getNotificationBody(): string {
  var messageInput: HTMLInputElement = document.querySelector("#message-input");
  return messageInput.value;
}


// send button modifications
var send_button_send_bg = "bg-indigo-600";
var send_button_send_hover = "hover:bg-indigo-700"
var send_button_pending_bg = "bg-gray-600";
var send_button_success_bg = "bg-green-600";


function setSendButtonToPending() {
  var sendButton: HTMLButtonElement = document.querySelector("#send-button");
  sendButton.innerHTML = "...";
  sendButton.disabled = true;
  sendButton.classList.remove(send_button_send_hover, send_button_send_bg);
  sendButton.classList.add(send_button_pending_bg);
}

function setSendButtonToNumber(nDevicesNotified: number) {
  var sendButton: HTMLButtonElement = document.querySelector("#send-button");
  sendButton.innerHTML = `${nDevicesNotified} devices notified...`;
  sendButton.classList.remove(send_button_pending_bg);
  sendButton.classList.add(send_button_success_bg);
}

function setSendButtonToSend() {
  var sendButton: HTMLButtonElement = document.querySelector("#send-button");
  sendButton.disabled = false;
  sendButton.classList.remove(send_button_success_bg);
  sendButton.classList.add(send_button_send_bg, send_button_send_hover);
  sendButton.innerHTML = "Send notification";
}

function sendPushNotifications(): Promise<boolean> {
  var csrfTokenInput : HTMLInputElement = document.querySelector("[name='csrfmiddlewaretoken']");// $("[name='csrfmiddlewaretoken']");
  var csrfToken = csrfTokenInput.value;
  var url = "/helloworld/send_notifications";
  var user_ids = getUserIds();
  // TODO: if notification body isn't given, don't allow the admin to send push notifications!
  var notification_body = getNotificationBody();
  var jsonBody = {"user_ids": user_ids,
                  "notification_body": notification_body};

  // Change the button to show something's happening
  setSendButtonToPending();

  const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

  var promise = fetch(url, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          "RequestVerificationToken": csrfToken,
      },
      body: JSON.stringify(jsonBody)
    })
    .then((response) => response.json())
    .then((json) => {
      console.log(json);
      setSendButtonToNumber(json["notified"]);
      setTimeout(setSendButtonToSend, 3000);
      return true;
    });
  
  return promise;
}

function initialize() {
  var sendButton: HTMLButtonElement = document.querySelector("#send-button");
  sendButton.addEventListener("click", sendPushNotifications);

  // Manage the user toggles.
  $(".toggle-btn").on("click", function (x) {
    var id = this.id;
    var spanId = id.replace("btn", "span");
    var spanElement: HTMLElement = document.querySelector(`#${spanId}`);

    if (this.classList.contains(enabled_btn_class))
    {
      this.classList.remove(enabled_btn_class);
      this.classList.add(disabled_btn_class);
      spanElement.classList.remove(enabled_span_class);
      spanElement.classList.add(disabled_span_class);
    }
    else
    {
      this.classList.add(enabled_btn_class);
      this.classList.remove(disabled_btn_class);
      spanElement.classList.add(enabled_span_class);
      spanElement.classList.remove(disabled_span_class);
    }
  });

  // handle search
  $("#search-input").on("keyup", function() {
    // get search term
    var element = this as HTMLInputElement;
    var searchTerm = element.value;
    // loop over user <li>s
    $(".user-name-element").each(function () {
      var element = this as HTMLInputElement;
      var matchesSearch = (searchTerm == "") || element.value.toLowerCase().includes(searchTerm);
      var elementId = this.id;
      var userId = parseInt(elementId.split('-')[1]);
      var liElement: HTMLElement = document.querySelector(`#li-${userId}`)
      liElement.hidden = !matchesSearch;
    })

  })
}

$( initialize )
