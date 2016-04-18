var Hephaestus = angular.module('Hephaestus', ['ngSanitize'])

Hephaestus.controller('OnlineController', function($scope, $sce) {
    var socket = io.connect('https://' + document.domain + ':' + location.port + '/heph')
    
    $scope.users = [];
    $scope.username = '';
    $scope.activePage = '';

  
    $scope.$watch('activePage', function() {
        console.log("Updating user", $scope.activePage, ' < location');
        console.log();
        socket.emit('newUser', $scope.activePage);
    });
   
    socket.on('connect', function() {
        console.log('connected');
    });
    
    socket.on('users', function(user) {
        console.log("it's trying to do something with ", user);
        var userPage = '<a href="/user/'+
            user.username + '"><div class="btn btn-sm onlineUser"><span>' + 
            user.username + '</span>&nbsp; <span>' + 
            user.location + '</span></div></a>';
        console.log(userPage);
        console.log($scope.users);
        $scope.users.push(userPage);
        $scope.$apply();
    });
    
    
    socket.on('newUser', function(user) {
        console.log("adding new user", user);
        var userPage = '<a href="/user/'+
            user.username + '"><div class="btn btn-sm onlineUser"><span>' + 
            user.username + '</span>&nbsp; <span>' + 
            user.location + '</span></div></a>';
        console.log(userPage);
        $scope.users.push(userPage);
        $scope.$apply();
    });
    
    socket.on('replaceUser', function(user) {
        console.log("replacing user", user);
        for (let i=0; i<$scope.users.length; i++) {
            console.log($scope.users[i]);
            if ($scope.users[i].username == user.username) {
                $scope.users[i] = user;
            }
        }
    });
    
    socket.on('deleteUser', function(user) {
        console.log("removing user", user);
        for (let i=0; i<$scope.users.length; i++) {
            console.log($scope.users[i]);
            if ($scope.users[i].username == user) {
                $scope.users.splice(i, 1);
            }
        }
    });
    
    $scope.logout = function logout() {
      console.log("logging out", $scope.userUsername);
      socket.emit('deleteUser', $scope.userUsername);
    };
/*
    $scope.newUser = function newUser() {
        console.log("Adding user", $scope.username);
        socket.emit('newUser', $scope.username);
    };
    
    
    $scope.updateUser = function updateUser() {
        console.log("Updating user", $scope.currentPage);
        socket.emit('users', $scope.currentPage);
    };
    
    $scope.getUsers = function getUsers() {
        socket.emit('users');
    };

    $scope.activePage = function activePage() {
        console.log('In activePage');
    };
*/
});