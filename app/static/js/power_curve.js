calculateSpeed = () => {
	const inputPower = document.calculateSpeedForm.userPower.value
	const speed = (-4.805e-05 * (inputPower ** 2)) + (0.1174 * inputPower) + 7.193 
	alert("Calculated speed is: " + Number(speed).toFixed(2) + " km/h")
}

calculatePower = () => {
	const inputSpeed = document.calculatePowerForm.userSpeed.value
	const power = (0.103  * (inputSpeed ** 2))+ ( 3.036 * inputSpeed ) + 25.93
	alert("Calculated power is: " + Number(power).toFixed(2) + " Watts")
}

calculateDistance = () => {
	const inputPower = document.calculateDistanceForm.userPower.value
	const inputTime = document.calculateDistanceForm.userTime.value
	const speed = (-4.805e-05 * (inputPower ** 2)) + (0.1174 * inputPower) + 7.193 
	time = inputTime.split(':');
	const distance = speed * (parseInt(time[0]) + (parseInt(time[1]) / 60) + (parseInt(time[2]) / 3600))
	alert("Calculated distance is: " + Number(distance).toFixed(2) + " km")
}
