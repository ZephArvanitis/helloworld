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

function initialize() {
  var sendButton: HTMLButtonElement = document.querySelector("#send-button");
  sendButton.addEventListener("click", trialAjaxCall);
}

$( initialize )
