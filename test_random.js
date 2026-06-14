console.log("===== LOGICAL OPERATORS =====");

let x = 7;

console.log(x > 5 && x < 10);
console.log(x < 5 || x === 7);
console.log(!(x === 10));


console.log("===== BASIC SORT =====");

let arr1 = [5,3,1,4,2];

arr1.sort();

console.log(arr1.join(", "));


console.log("===== SORT ASCENDING CALLBACK =====");

let arr2 = [5,3,1,4,2];

arr2.sort((a,b)=>a-b);

console.log(arr2.join(", "));


console.log("===== SORT DESCENDING CALLBACK =====");

let arr3 = [5,3,1,4,2];

arr3.sort((a,b)=>b-a);

console.log(arr3.join(", "));


console.log("===== SORT EDGE CASE =====");

let arr4 = [10,2,1,30,5];

arr4.sort((a,b)=>a-b);

console.log(arr4.join(", "));


console.log("===== MAP =====");

let nums1 = [1,2,3,4];

let doubled = nums1.map(x => x * 2);

console.log(doubled.join(", "));


console.log("===== FILTER =====");

let nums2 = [1,2,3,4,5,6];

let filtered = nums2.filter(x => x > 3);
console.log("===== SHIFT / UNSHIFT =====");

let arr = [1,2,3,4];

arr.shift();
console.log(arr.join(", "));

arr.unshift(0);
console.log(arr.join(", "));


console.log("===== SPLICE =====");

let arr2 = [1,2,3,4,5];

arr2.splice(1,2);

console.log(arr2.join(", "));


console.log("===== SPREAD =====");

let arr3 = [1,2,3];

let arr4 = [...arr3, 4, 5];

console.log(arr4.join(", "));


console.log("===== REST PARAMS =====");

function sum(...nums) {
    return nums.reduce((acc,x)=>acc+x,0);
}

console.log(sum(1,2,3,4));


console.log("===== DATE =====");

let d = new Date();

console.log(d.getFullYear() > 2020);
console.log(d.getMonth() >= 0);
console.log(d.getDate() > 0);


console.log("===== RANDOM =====");

let r = Math.random();

console.log(r >= 0 && r <= 1);