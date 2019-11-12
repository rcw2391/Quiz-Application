checkTime = () => {
    timeLimitInput = document.getElementById('time_limit_input');
    time = timeLimitInput.value;
    if(time > 120) {
        timeLimitInput.value = 120;
        alert('Max time is 120 minutes.')
    }
    if(time < 0){
        timeLimitInput.value = 0;
        alert('Minimum time is 0 minutes.')
    }
}