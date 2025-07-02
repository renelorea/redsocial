-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 01-07-2025 a las 03:02:15
-- Versión del servidor: 10.4.28-MariaDB
-- Versión de PHP: 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `redsocial`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cosas_en_comun`
--

CREATE TABLE `cosas_en_comun` (
  `id` int(11) NOT NULL,
  `persona1_id` int(11) DEFAULT NULL,
  `persona2_id` int(11) DEFAULT NULL,
  `interes` text DEFAULT NULL,
  `peso` int(11) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `cosas_en_comun`
--

INSERT INTO `cosas_en_comun` (`id`, `persona1_id`, `persona2_id`, `interes`, `peso`) VALUES
(20, 1, 2, NULL, 1),
(21, 3, 1, NULL, 1),
(22, 6, 1, NULL, 12),
(23, 7, 1, NULL, 13),
(24, 6, 1, NULL, 18);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `dislikes`
--

CREATE TABLE `dislikes` (
  `id` int(11) NOT NULL,
  `publicacion_id` int(11) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `id_persona` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `dislikes`
--

INSERT INTO `dislikes` (`id`, `publicacion_id`, `id_usuario`, `id_persona`) VALUES
(1, 5, 1, NULL),
(2, 5, 1, NULL),
(3, 5, 1, NULL),
(4, 3, 1, NULL),
(5, 3, 1, NULL),
(6, 3, 1, NULL),
(7, 5, 2, NULL),
(8, 5, 2, NULL),
(9, 4, 2, NULL),
(10, 3, 2, NULL),
(11, 3, 2, NULL),
(12, 3, 2, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `likes`
--

CREATE TABLE `likes` (
  `id` int(11) NOT NULL,
  `publicacion_id` int(11) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `id_persona` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `likes`
--

INSERT INTO `likes` (`id`, `publicacion_id`, `id_usuario`, `id_persona`) VALUES
(1, 5, 1, NULL),
(2, 5, 1, NULL),
(3, 4, 1, NULL),
(4, 4, 1, NULL),
(5, 3, 1, NULL),
(6, 3, 1, NULL),
(7, 5, 1, NULL),
(8, 4, 1, NULL),
(9, 3, 1, NULL),
(10, 2, 1, NULL),
(11, 5, 1, NULL),
(12, 3, 1, NULL),
(13, 3, 1, NULL),
(14, 5, 2, NULL),
(15, 5, 2, NULL),
(16, 4, 2, NULL),
(17, 3, 2, NULL),
(18, 1, 2, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `personas`
--

CREATE TABLE `personas` (
  `id` int(11) NOT NULL,
  `nombre` text DEFAULT NULL,
  `edad` int(11) DEFAULT NULL,
  `ciudad` text DEFAULT NULL,
  `usuario` varchar(20) DEFAULT NULL,
  `password` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `personas`
--

INSERT INTO `personas` (`id`, `nombre`, `edad`, `ciudad`, `usuario`, `password`) VALUES
(1, 'Ana', 25, 'CDMX', 'usuario1', 'user1'),
(2, 'Luis', 30, 'CDMX', 'usuario2', 'user2'),
(3, 'Sofía', 28, 'CDMX', 'usuario3', 'user3'),
(4, 'Carlos', 35, 'CDMX', 'usuario4', 'user4'),
(5, 'Elena', 22, 'CDMX', 'usuario5', 'user5'),
(6, 'Diego', 27, 'CDMX', 'usuario6', 'user6'),
(7, 'Valeria', 29, 'CDMX', 'usuario7', 'user7'),
(8, 'Rene', 44, NULL, 'usuario8', 'user8'),
(9, 'admin', 43, 'CDMX', 'admin', 'admin');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `publicaciones`
--

CREATE TABLE `publicaciones` (
  `id` int(11) NOT NULL,
  `id_autor` int(11) DEFAULT NULL,
  `contenido` text DEFAULT NULL,
  `fecha` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `publicaciones`
--

INSERT INTO `publicaciones` (`id`, `id_autor`, `contenido`, `fecha`) VALUES
(1, 1, '¡Me encanta el cine!', '2025-06-01'),
(2, 3, '¿Quién quiere viajar a Oaxaca?', '2025-06-05'),
(3, 6, 'Nuevo torneo de videojuegos ', '2025-06-10'),
(4, 7, 'Recomiendo este libro ', '2025-06-12'),
(5, 6, 'lo major de lo major del Futbol', '2025-06-25');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `cosas_en_comun`
--
ALTER TABLE `cosas_en_comun`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `dislikes`
--
ALTER TABLE `dislikes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `publicacion_id` (`publicacion_id`);

--
-- Indices de la tabla `likes`
--
ALTER TABLE `likes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `publicacion_id` (`publicacion_id`);

--
-- Indices de la tabla `personas`
--
ALTER TABLE `personas`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `publicaciones`
--
ALTER TABLE `publicaciones`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `cosas_en_comun`
--
ALTER TABLE `cosas_en_comun`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT de la tabla `dislikes`
--
ALTER TABLE `dislikes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `likes`
--
ALTER TABLE `likes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT de la tabla `personas`
--
ALTER TABLE `personas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `publicaciones`
--
ALTER TABLE `publicaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `dislikes`
--
ALTER TABLE `dislikes`
  ADD CONSTRAINT `dislikes_ibfk_1` FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones` (`id`);

--
-- Filtros para la tabla `likes`
--
ALTER TABLE `likes`
  ADD CONSTRAINT `likes_ibfk_1` FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
