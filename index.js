async function getCars() {
  try {
    const response = await fetch("https://vpic.nhtsa.dot.gov/api/vehicles/getmodelsformake/toyota?format=json");
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

getCars();